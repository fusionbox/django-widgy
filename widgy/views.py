"""
Resource views that can be included to enable a REST style API
for Widgy nodes and Content objects.
"""
from django.http import Http404
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
from django.views.generic import DetailView
from django.views.generic.detail import SingleObjectMixin
from django.db.models import get_model

from fusionbox.views.rest import RestView

from widgy.models import Node
from widgy.exceptions import InvalidTreeMovement
from widgy.utils import extract_id
from widgy.signals import tree_changed


class WidgyViewMixin(object):
    site = None

    def auth(self, request, *args, **kwargs):
        self.site.authorize(request)


class WidgyView(WidgyViewMixin, RestView):
    pass


class ContentView(WidgyView):
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
        return self.render_to_response(obj.to_json(self.site))

    def put(self, request, app_label, object_name, object_pk):
        obj = self.get_object(app_label, object_name, object_pk)
        data = self.data()
        form = obj.get_form_class(request)(data=data or None, instance=obj)
        if not form.is_valid():
            raise ValidationError(form.errors)
        form.save()

        tree_changed.send(sender=self, node=obj.node, content=obj)

        return self.render_to_response(form.instance.to_json(self.site),
                                       status=200)


class NodeView(WidgyView):
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
        return self.render_to_response(node.to_json(self.site))

    def post(self, request, node_pk=None):
        data = self.data()
        app_label, model = data['__class__'].split('.')
        content_class = get_model(app_label, model)
        if not content_class:
            raise Http404

        try:
            right = get_object_or_404(Node, pk=extract_id(data['right_id']))
            content = right.content.add_sibling(self.site, content_class)
        except Http404:
            parent = get_object_or_404(Node, pk=extract_id(data['parent_id']))
            content = parent.content.add_child(self.site, content_class)

        tree_changed.send(sender=self, node=content.node, content=content)

        return self.render_to_response(content.node.to_json(self.site),
                                       status=201)

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
            node.reposition(self.site, right=right)
        except Node.DoesNotExist:
            try:
                parent = Node.objects.get(pk=extract_id(data['parent_id']))
                node.reposition(self.site, parent=parent)
            except Node.DoesNotExist:
                raise Http404

        tree_changed.send(sender=self, node=node, content=node.content)

        return self.render_to_response(None, status=200)

    def delete(self, request, node_pk):
        node = get_object_or_404(Node, pk=node_pk)

        if not node.content.deletable:
            raise InvalidTreeMovement({'message': "You can't delete me"})

        tree_changed.send(sender=self, node=node, content=node.content)
        node.delete()

        return self.render_to_response(None)

    def options(self, request, node_pk=None):
        response = super(NodeView, self).options(request, node_pk)

        if not node_pk:
            response['Allow'] = 'POST'

        return response


class ShelfView(WidgyView):
    """
    For a given node, returns a mapping of node urls to lists of content
    classes that can be their children.::

        {
            node_url: [content classes]
            node_url: [content classes]
        }

    Used on the frontend to populate the shelf.
    """

    def serialize_content_classes(self, obj):
        """
        The built-in json encoder doesn't support class_to_json, so
        we'll do it manually.
        """
        res = {}
        for node, classes in obj.iteritems():
            res[node.get_api_url(self.site)] = [i.class_to_json(self.site) for i in classes]
        return res

    def get(self, request, node_pk):
        content_classes = self.site.get_all_content_classes()
        node = get_object_or_404(Node, pk=node_pk)
        node.prefetch_tree()
        content_classes = node.filter_child_classes_recursive(self.site, content_classes)
        return self.render_to_response(
            self.serialize_content_classes(content_classes))


class NodeSingleObjectMixin(SingleObjectMixin):
    model = Node
    pk_url_kwarg = 'node_pk'


class NodeEditView(WidgyViewMixin, NodeSingleObjectMixin, DetailView):
    """
    The only TemplateView in widgy: The interface for popped out node editing.
    """

    template_name = 'widgy/views/edit_node.html'

    def dispatch(self, *args, **kwargs):
        self.auth(*args, **kwargs)
        return super(NodeEditView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs = super(NodeEditView, self).get_context_data(**kwargs)
        kwargs['html_id'] = 'node_%s' % (self.object.pk)
        kwargs['node_dict'] = self.object.to_json(self.site)
        return kwargs


class NodeTemplatesView(NodeSingleObjectMixin, WidgyView):
    """
    Gets the dynamic [needing request] templates for a node.
    """

    def get(self, request, *args, **kwargs):
        node = self.object = self.get_object()
        return self.render_to_response(node.content.get_templates(request))


class NodeParentsView(NodeSingleObjectMixin, WidgyView):
    """
    Given a node, where in its tree can it be moved?
    """

    def get(self, request, *args, **kwargs):
        node = self.object = self.get_object()
        node.prefetch_tree()
        possible_parents = node.possible_parents(self.site, node.get_root())
        return self.render_to_response([i.get_api_url(self.site) for i in possible_parents])
