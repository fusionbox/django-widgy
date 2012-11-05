import json
from decimal import Decimal

from django.core.exceptions import PermissionDenied
from django.core.exceptions import ValidationError
from django.http import HttpResponse, Http404
from django.views.generic.base import View
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType

from widgy.models import Node, Content, InvalidTreeMovement


def more_json(obj):
    """
    Allows decimals and objects with `to_json` methods to be serialized.
    """
    if isinstance(obj, Decimal):
        return str(obj)
    if hasattr(obj, 'to_json'):
        return obj.to_json()
    raise TypeError("%r is not JSON serializable" % (obj,))


class JsonResponseMixin(object):
    def render_to_response(self, obj, **response_kwargs):
        return HttpResponse(self.serialize(obj), content_type='application/json', **response_kwargs)

    def serialize(self, obj):
        try:
            obj = obj.to_json()
        except AttributeError:
            pass

        try:
            obj = [i.to_json() for i in obj]
        except (AttributeError, TypeError):
            pass

        return json.dumps(obj, default=more_json)

    def http_method_not_allowed(self, *args, **kwargs):
        resp = super(JsonResponseMixin, self).http_method_not_allowed(*args, **kwargs)
        resp['Content-Type'] = 'application/json'

        return resp


class JsonRequestMixin(object):
    def data(self):
        if self.request.method == 'GET':
            return self.request.GET
        else:
            assert self.request.META['CONTENT_TYPE'].startswith('application/json')
            return json.loads(self.request.body)


class RestView(JsonResponseMixin, JsonRequestMixin, View):
    def auth(*args, **kwargs):
        raise NotImplementedError("If you really want no authentication, override this method")

    def dispatch(self, *args, **kwargs):
        try:
            self.auth(*args, **kwargs)
            return super(RestView, self).dispatch(*args, **kwargs)
        except ValidationError as e:
            return self.render_to_response(e.message_dict, status=409)
        except Http404 as e:
            return self.render_to_response(None, status=404)
        except PermissionDenied as e:
            return self.render_to_response(str(e), status=403)
        except ValueError as e:
            return self.render_to_response(str(e), status=400)

    def options(self, request, *args, **kwargs):
        allow = []
        for method in self.http_method_names:
            if hasattr(self, method):
                allow.append(method.upper())
        r = self.render_to_response(None)
        r['Allow'] = ','.join(allow)
        return r


class ContentView(RestView):
    def auth(*args, **kwargs):
        pass

    def get_object(self, app_label, object_name, object_pk):
        return ContentType.objects.get(
                    model=object_name,
                    app_label=app_label
                ).get_object_for_this_type(
                    pk=object_pk)

    def get(self, request, app_label, object_name, object_pk):
        obj = self.get_object(app_label, object_name, object_pk)
        return self.render_to_response(obj)

    # TODO: stupid implementation
    # only for existing objects right now
    def put(self, request, app_label, object_name, object_pk):
        obj = self.get_object(app_label, object_name, object_pk)
        data = self.data()
        for field in obj._meta.fields:
            if not field.editable:
                continue
            if field.attname in data:
                setattr(obj, field.attname, data[field.attname])
        obj.save()

        return self.render_to_response(obj, status=200)


content = ContentView.as_view()

def extract_id(url):
    return url and url.split('/')[-2]

class NodeView(RestView):
    def auth(*args, **kwargs):
        pass

    def put(self, request, node_pk):
        """
        If you put with a right_id, then your node will be placed immediately
        to the right of the node corresponding with the right_id.

        If you put with a parent_id, then your node will be placed as the
        first-child of the node corresponding with the parent_id.
        """
        # TODO: put this in the model
        node = get_object_or_404(Node, pk=node_pk)
        data = self.data()

        try:
            right = Node.objects.get(pk=extract_id(data['right_id']))
            node.reposition(right=right)
        except Node.DoesNotExist:
            try:
                parent = Node.objects.get(pk=extract_id(data['parent_id']))
                node.reposition(parent=parent)
            except Node.DoesNotExist:
                raise Http404

        return self.render_to_response(None, status=200)

    def delete(self, request, node_pk):
        node = get_object_or_404(Node, pk=node_pk)

        if not node.content.deletable:
            raise InvalidTreeMovement({'message': "You can't delete me"})

        node.delete()

        return self.render_to_response(None)


node = NodeView.as_view()


class CreateNodeView(RestView):
    def auth(*args, **kwargs):
        pass

    def post(self, request):
        data = self.data()
        app_label, model = data['__class__'].split('.')
        content_class = get_object_or_404(ContentType, model=model, app_label=app_label).model_class()

        try:
            right = get_object_or_404(Node, pk=extract_id(data['right_id']))
            content = right.content.add_sibling(content_class)
        except Http404:
            parent = get_object_or_404(Node, pk=extract_id(data['parent_id']))
            content = parent.content.add_child(content_class)

        return self.render_to_response(content.node, status=201)


create_node = CreateNodeView.as_view()


class ChildrenView(RestView):
    def auth(*args, **kwargs):
        pass

    def get(self, request, node_pk):
        node = get_object_or_404(Node, pk=node_pk)
        content_classes = Content.all_concrete_subclasses()
        content_classes = node.filter_child_classes(content_classes)

        return self.render_to_response([i.class_to_json() for i in content_classes])

children = ChildrenView.as_view()


class RecursiveChildrenView(RestView):
    def auth(*args, **kwargs):
        pass

    def get(self, request, node_pk=None):
        content_classes = Content.all_concrete_subclasses()
        if node_pk:
            node = get_object_or_404(Node, pk=node_pk)
            content_classes = node.filter_child_classes_recursive(content_classes)
        return self.render_to_response([i.class_to_json() for i in content_classes])

recursive_children = RecursiveChildrenView.as_view()
