"""
Resource views that can be included to enable a REST style API
for Widgy nodes and Content objects.
"""
from django.http import Http404
from django.conf import settings
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
from django.views.generic import DetailView
from django.views.generic.detail import SingleObjectMixin

from fusionbox.views.rest import RestView

from widgy.models import Node, Content, InvalidTreeMovement
from widgy.utils import extract_id, fancy_import


class AuthorizedRestView(RestView):
    def auth(self, request, *args, **kwargs):
        if getattr(settings, 'WIDGY_AUTH_MODULE', None):
            fancy_import(settings.WIDGY_AUTH_MODULE).authorize(request)


class ContentView(AuthorizedRestView):
    """
    General purpose resource for :class:`widgy.models.Content` objects.

    **Supported Methods**:
        :get: Fetch a :class:`widgy.models.Content` object.
        :put: Make changes to a :class:`widgy.models.Content` object.

    .. todo::
        change ``put`` method to be more generic.
    """

    def get_object(self, app_label, object_name, object_pk):
        """
        Resolves ``app_label``, ``object_name``, and ``object_pk`` to a
        :class:`widgy.models.Content` instance.
        """
        return (
            ContentType.objects.get(model=object_name, app_label=app_label)
            .get_object_for_this_type(pk=object_pk)
        )

    def get(self, request, app_label, object_name, object_pk):
        obj = self.get_object(app_label, object_name, object_pk)
        return self.render_to_response(obj)

    def put(self, request, app_label, object_name, object_pk):
        obj = self.get_object(app_label, object_name, object_pk)
        data = self.data()
        form = obj.get_form_class(request)(data=data or None, instance=obj)
        if not form.is_valid():
            raise ValidationError(form.errors)
        form.save()
        return self.render_to_response(form.instance, status=200)


class NodeView(AuthorizedRestView):
    """
    General purpose resource for updating, deleting, and repositioning
    :class:`widgy.models.Node` objects.

    **Supported Methods**:
        :post: Create a new :class:`widgy.models.Node` object.  This method
            requires that ``__class__`` is passed in the JSON request as a
            parameter.  ``__class__`` is expected to be a ``.`` separated
            string of ``app_label.model_classname``.
        :delete: Delete a :class:`widgy.models.Node` object.
        :put: Make changes to a :class:`widgy.models.Node` object.  This method
            also supports repositioning a node to the the left of new sibling by
            supplying a ``right_id`` in the request.

    """
    def get(self, request, node_pk):
        node = get_object_or_404(Node, pk=node_pk)
        return self.render_to_response(node)

    def post(self, request, node_pk=None):
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

    def put(self, request, node_pk):
        """
        If you put with a right_id, then your node will be placed immediately
        to the right of the node corresponding with the right_id.

        If you put with a parent_id, then your node will be placed as the
        first-child of the node corresponding with the parent_id.

        .. todo::
            put this in the model
        """
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


class ChildrenView(AuthorizedRestView):
    """
    Resource that retrieves all the valid children classes for the given node
    instance.

    **Supported Methods**:
        :get: Get all the valid content classes for the given node instance.
    """
    def get(self, request, node_pk):
        node = get_object_or_404(Node, pk=node_pk)
        content_classes = Content.all_concrete_subclasses()
        content_classes = node.filter_child_classes(content_classes)

        return self.render_to_response([i.class_to_json() for i in content_classes])


class RecursiveChildrenView(AuthorizedRestView):
    """
    Resource that retrieves not only the valid content classes, but also the
    valid content classes of the node's children.

    **Supported Methods**:
        :get: Get all the child classes of the node instance, and all its
            children.
    """
    def get(self, request, node_pk):
        content_classes = Content.all_concrete_subclasses()
        node = get_object_or_404(Node, pk=node_pk)
        content_classes = node.filter_child_classes_recursive(content_classes)
        res_dict = {}
        for node, class_list in content_classes.iteritems():
            if node.content.pop_out != 2 or str(node.pk) == node_pk:
                for cls in class_list:
                    res_dict.setdefault(cls, cls.class_to_json())
                    res_dict[cls].setdefault('possible_parent_nodes', [])
                    res_dict[cls]['possible_parent_nodes'].append(node.get_api_url())

        return self.render_to_response(res_dict.values())

children = ChildrenView.as_view()
recursive_children = RecursiveChildrenView.as_view()
content = ContentView.as_view()
node = NodeView.as_view()


class NodeEditView(DetailView):
    template_name = 'widgy/edit_node.html'
    model = Node
    pk_url_kwarg = 'node_pk'

    def get_context_data(self, **kwargs):
        kwargs = super(NodeEditView, self).get_context_data(**kwargs)
        kwargs['html_id'] = 'node_%s' % (self.object.pk)
        return kwargs

edit_node = NodeEditView.as_view()


class NodeTemplateView(SingleObjectMixin, AuthorizedRestView):
    model = Node
    pk_url_kwarg = 'node_pk'

    def get(self, request, *args, **kwargs):
        node = self.object = self.get_object()
        return self.render_to_response(node.content.get_templates(request))

node_templates = NodeTemplateView.as_view()
