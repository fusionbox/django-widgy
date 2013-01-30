from django.conf.urls import patterns, url
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied

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
)
from widgy.exceptions import (
    MutualRejection,
    ParentWasRejected,
    ChildWasRejected,
)


class WidgySite(object):
    def __init__(self):
        self.node_view = self.get_node_view()
        self.content_view = self.get_content_view()
        self.shelf_view = self.get_shelf_view()
        self.node_edit_view = self.get_node_edit_view()
        self.node_templates_view = self.get_node_templates_view()
        self.node_parents_view = self.get_node_parents_view()
        self.commit_view = self.get_commit_view()
        self.history_view = self.get_history_view()
        self.revert_view = self.get_revert_view()
        self.diff_view = self.get_diff_view()

    def get_registry(self):
        return registry

    def get_all_content_classes(self):
        return self.get_registry().keys()

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
            url('^diff/(?P<before_pk>[^/]+)/(?P<after_pk>[^/]+)/$', self.diff_view),
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

    def authorize(self, request):
        if not request.user.is_authenticated():
            raise PermissionDenied

    def get_node_view(self):
        return NodeView.as_view(site=self)

    def get_content_view(self):
        return ContentView.as_view(site=self)

    def get_shelf_view(self):
        return ShelfView.as_view(site=self)

    def get_node_edit_view(self):
        return NodeEditView.as_view(site=self)

    def get_node_templates_view(self):
        return NodeTemplatesView.as_view(site=self)

    def get_node_parents_view(self):
        return NodeParentsView.as_view(site=self)

    def get_commit_view(self):
        return CommitView.as_view(site=self)

    def get_history_view(self):
        return HistoryView.as_view(site=self)

    def get_revert_view(self):
        return RevertView.as_view(site=self)

    def get_diff_view(self):
        return DiffView.as_view(site=self)

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
