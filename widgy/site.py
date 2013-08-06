from django.conf.urls import patterns, url
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.contrib.staticfiles import finders
from django.utils.functional import cached_property

from widgy import registry
from widgy.views import (
    NodeView,
    ContentView,
    ShelfView,
    NodeEditView,
    NodeTemplatesView,
    NodeParentsView,
    CommitView,
    HistoryView,
    RevertView,
    DiffView,
    ResetView,
)
from widgy.exceptions import (
    MutualRejection,
    ParentWasRejected,
    ChildWasRejected,
)


class WidgySite(object):
    def get_registry(self):
        return registry

    def get_all_content_classes(self):
        return self.get_registry()

    def get_urls(self):
        urlpatterns = patterns('',
            url('^node/$', self.node_view),
            url('^node/(?P<node_pk>[^/]+)/$', self.node_view),
            url('^node/(?P<node_pk>[^/]+)/available-children-recursive/$', self.shelf_view),
            url('^node/(?P<node_pk>[^/]+)/edit/$', self.node_edit_view),
            url('^node/(?P<node_pk>[^/]+)/templates/$', self.node_templates_view),
            url('^node/(?P<node_pk>[^/]+)/possible-parents/$', self.node_parents_view),
            url('^contents/(?P<app_label>[A-z_][\w_]*)/(?P<object_name>[A-z_][\w_]*)/(?P<object_pk>[^/]+)/$', self.content_view),

            # versioning
            url('^revert/(?P<pk>[^/]+)/(?P<commit_pk>[^/]+)/$', self.revert_view),
            url('^commit/(?P<pk>[^/]+)/$', self.commit_view),
            url('^history/(?P<pk>[^/]+)/$', self.history_view),
            url('^reset/(?P<pk>[^/]+)/$', self.reset_view),
            url('^diff/$', self.diff_view),
        )
        return urlpatterns

    @property
    def urls(self):
        return self.get_urls()

    def reverse(self, *args, **kwargs):
        """
        We tried to use namespaced URLs per site just like ModelAdmins,
        however, as we refer to the views by their function objects, we can't
        use namespaces because there is a bug in Django:

        https://code.djangoproject.com/ticket/17914

        We should use named URLs instead of function references, but we
        couldn't get that working.
        """
        return reverse(*args, **kwargs)

    def get_view_instance(self, view):
        try:
            return view.view_instance
        except AttributeError:
            raise ValueError("View does not inherit from WidgyViewMixin")

    def authorize_view(self, request, view):
        if not request.user.is_authenticated():
            raise PermissionDenied

    def has_add_permission(self, request, content_class):
        return request.user.has_perm('%s.%s' % (content_class._meta.app_label, content_class._meta.get_add_permission()))

    def has_change_permission(self, request, obj_or_class):
        return request.user.has_perm('%s.%s' % (obj_or_class._meta.app_label, obj_or_class._meta.get_change_permission()))

    def has_delete_permission(self, request, obj_or_class):
        def has_perm(o):
            return request.user.has_perm('%s.%s' % (o._meta.app_label, o._meta.get_delete_permission()))

        if isinstance(obj_or_class, type):
            return has_perm(obj_or_class)
        else:
            return all(map(has_perm, obj_or_class.depth_first_order()))

    # These must return the same instance throughout the whole lifetime
    # of the widgy site for reverse to work.
    @cached_property
    def node_view(self):
        return NodeView.as_view(site=self)

    @cached_property
    def content_view(self):
        return ContentView.as_view(site=self)

    @cached_property
    def shelf_view(self):
        return ShelfView.as_view(site=self)

    @cached_property
    def node_edit_view(self):
        return NodeEditView.as_view(site=self)

    @cached_property
    def node_templates_view(self):
        return NodeTemplatesView.as_view(site=self)

    @cached_property
    def node_parents_view(self):
        return NodeParentsView.as_view(site=self)

    @cached_property
    def commit_view(self):
        return CommitView.as_view(site=self)

    @cached_property
    def history_view(self):
        return HistoryView.as_view(site=self)

    @cached_property
    def revert_view(self):
        return RevertView.as_view(site=self)

    @cached_property
    def diff_view(self):
        return DiffView.as_view(site=self)

    @cached_property
    def reset_view(self):
        return ResetView.as_view(site=self)

    def valid_parent_of(self, parent, child_class, child=None):
        return parent.valid_parent_of(child_class, child)

    def valid_child_of(self, parent, child_class, child=None):
        return child_class.valid_child_of(parent, child)

    def validate_relationship(self, parent, child):
        if isinstance(child, type):
            child_class = child
            child = None
        else:
            child_class = type(child)

        bad_child = not self.valid_parent_of(parent, child_class, child)
        bad_parent = not self.valid_child_of(parent, child_class, child)

        if bad_parent and bad_child:
            raise MutualRejection
        elif bad_parent:
            raise ParentWasRejected
        elif bad_child:
            raise ChildWasRejected

    def get_version_tracker_model(self):
        from widgy.models import VersionTracker
        return VersionTracker

    def filter_existing_staticfiles(self, filename):
        path = finders.find(filename)
        return bool(path)

    def find_media_files(self, extension, hierarchy=['widgy/{app_label}/{module_name}{extension}']):
        files = set()
        for widget in self.get_all_content_classes():
            files.update(widget.get_templates_hierarchy(
                hierarchy=hierarchy,
                extension=extension,
            ))
        return filter(self.filter_existing_staticfiles, files)

    @cached_property
    def scss_files(self):
        return self.find_media_files('.scss')

    @cached_property
    def js_files(self):
        return self.find_media_files('.js')

    @cached_property
    def admin_scss_files(self):
        return self.find_media_files(
            extension='.scss',
            hierarchy=[
                'widgy/{app_label}/{module_name}.admin{extension}',
                'widgy/{app_label}/admin{extension}',
            ])
