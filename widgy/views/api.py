"""
Resource views that can be included to enable a REST style API
for Widgy nodes and Content objects.
"""
from functools import partial

from django.http import Http404
from django.core.exceptions import ValidationError, PermissionDenied
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
from django.views.generic import DetailView
from django.views.generic.detail import SingleObjectMixin
from django.db.models import ProtectedError
from django.utils.translation import ugettext as _

try:
    from django.apps import apps
    get_model = apps.get_model
    del apps
except ImportError:
    # Django < 1.8
    from django.db.models import get_model

from argonauts.views import RestView

from widgy.models import Node
from widgy.exceptions import InvalidTreeMovement
from widgy.utils import extract_id
from widgy.views.base import WidgyViewMixin, AuthorizedMixin


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
    def dispatch(self, request, app_label, object_name, object_pk):
        return super(ContentView, self).dispatch(request, app_label, object_name, object_pk)

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
        if not self.site.has_change_permission(request, obj):
            raise PermissionDenied(_("You don't have permission to edit this widget."))

        data = self.data()['attributes']
        form = obj.get_form(request, data=data)
        if not form.is_valid():
            raise ValidationError(form.errors)
        form.save()
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
    def render_as_node(self, obj, *args, **kwargs):
        obj = {'node': obj}

        compatibility_node_url = self.request.GET.get('include_compatibility_for', None)
        if compatibility_node_url:
            node = get_object_or_404(Node, pk=extract_id(compatibility_node_url))
            obj['compatibility'] = ShelfView.get_compatibility_data(self.site, self.request, node)

        return self.render_to_response(obj, *args, **kwargs)

    def get(self, request, node_pk):
        node = get_object_or_404(Node, pk=node_pk)
        node.prefetch_tree()
        return self.render_as_node(node.to_json(self.site))

    def post(self, request, node_pk=None):
        data = self.data()
        app_label, model = data['__class__'].split('.')
        try:
            content_class = get_model(app_label, model)
        except LookupError:
            raise Http404

        try:
            right = get_object_or_404(Node, pk=extract_id(data['right_id']))
            parent = right.get_parent()
            create_content = right.content.add_sibling
        except Http404:
            parent = get_object_or_404(Node, pk=extract_id(data['parent_id']))
            create_content = parent.content.add_child

        if not self.site.has_add_permission(request, parent.content, content_class):
            raise PermissionDenied(_("You don't have permission to add this widget."))

        content = create_content(self.site, content_class)

        return self.render_as_node(content.node.to_json(self.site),
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

        if not self.site.has_change_permission(request, node.content):
            raise PermissionDenied(_("You don't have permission to move this widget."))
        if not node.content.draggable:
            raise InvalidTreeMovement({'message': "You can't move me"})

        try:
            right = Node.objects.get(pk=extract_id(data['right_id']))
            node.content.reposition(self.site, right=right.content)
        except Node.DoesNotExist:
            try:
                parent = Node.objects.get(pk=extract_id(data['parent_id']))
                node.content.reposition(self.site, parent=parent.content)
            except Node.DoesNotExist:
                raise Http404

        # We have to refetch before returning because treebeard doesn't
        # update the in-memory instance, only the database, see
        # <https://tabo.pe/projects/django-treebeard/docs/tip/caveats.html#raw-queries>
        node = Node.objects.get(pk=node.pk)
        node.prefetch_tree()

        return self.render_as_node(node.to_json(self.site), status=200)

    def delete(self, request, node_pk):
        node = get_object_or_404(Node, pk=node_pk)

        if not self.site.has_delete_permission(request, node.content):
            raise PermissionDenied(_("You don't have permission to delete this widget."))
        if not node.content.deletable:
            raise InvalidTreeMovement({'message': "You can't delete me"})

        try:
            node.content.delete()
            return self.render_as_node(None)
        except ProtectedError as e:
            raise ValidationError({'message': e.args[0]})

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

    @staticmethod
    def serialize_content_classes(site, obj):
        """
        The built-in json encoder doesn't support class_to_json, so
        we'll do it manually.
        """
        res = {}
        for node, classes in obj.items():
            res[node.get_api_url(site)] = [i.class_to_json(site) for i in classes]
        return res

    @staticmethod
    def get_compatibility_data(site, request, root_node):
        root_node.maybe_prefetch_tree()
        parent = root_node.content
        content_classes = site.get_all_content_classes()
        content_classes = [c for c in content_classes
                           if site.has_add_permission(request, parent, c)]
        content_classes = root_node.filter_child_classes_recursive(site, content_classes)
        return ShelfView.serialize_content_classes(site, content_classes)

    def get(self, request, node_pk):
        node = get_object_or_404(Node, pk=node_pk)
        return self.render_to_response(self.get_compatibility_data(self.site, request, node))


class NodeSingleObjectMixin(SingleObjectMixin):
    model = Node
    pk_url_kwarg = 'node_pk'


class NodeEditView(NodeSingleObjectMixin, AuthorizedMixin, DetailView):
    """
    The only TemplateView in widgy: The interface for popped out node editing.
    """

    template_name = 'widgy/views/edit_node.html'

    def get_context_data(self, **kwargs):
        if not self.site.has_change_permission(self.request, self.object):
            raise PermissionDenied(_("You don't have permission to edit this widget."))
        kwargs = super(NodeEditView, self).get_context_data(**kwargs)
        self.object.prefetch_tree()
        kwargs.update(
            html_id='node_%s' % (self.object.pk),
            node_dict=self.object.to_json(self.site),
            api_url=reverse(self.site.node_view),
            site=self.site,
        )
        return kwargs


class NodeTemplatesView(NodeSingleObjectMixin, WidgyView):
    """
    Gets the dynamic [needing request] templates for a node.
    """
    def get(self, request, *args, **kwargs):
        node = self.object = self.get_object()
        if not self.site.has_change_permission(request, node.content):
            raise PermissionDenied(_("You don't have permission to edit this widget."))
        return self.render_to_response(node.content.get_templates(request))


class NodeParentsView(NodeSingleObjectMixin, WidgyView):
    """
    Given a node, where in its tree can it be moved?
    """

    def get(self, request, *args, **kwargs):
        node = self.object = self.get_object()
        if not self.site.has_change_permission(request, node.content):
            raise PermissionDenied(_("You don't have permission to move this widget."))
        node.prefetch_tree()
        possible_parents = node.possible_parents(self.site, node.get_root())
        return self.render_to_response([i.get_api_url(self.site) for i in possible_parents])
