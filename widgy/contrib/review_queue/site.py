from django.conf.urls import patterns, url
from django.utils.functional import cached_property

from widgy.site import WidgySite
from widgy.views import HistoryView

from .views import (
    ApproveView,
    ReviewedCommitView,
    UnapproveView,
    UndoApprovalsView,
)


class ReviewedWidgySite(WidgySite):
    def __init__(self, *args, **kwargs):
        super(ReviewedWidgySite, self).__init__(*args, **kwargs)

    def get_version_tracker_model(self):
        from .models import ReviewedVersionTracker
        return ReviewedVersionTracker

    def get_urls(self):
        return super(ReviewedWidgySite, self).get_urls() + patterns('',
            url('^approve/(?P<pk>[^/]+)/(?P<commit_pk>[^/]+)/$', self.approve_view),
            url('^unapprove/(?P<pk>[^/]+)/(?P<commit_pk>[^/]+)/$', self.unapprove_view),
            url('^undo-approvals/$', self.undo_approvals_view),
        )

    @cached_property
    def commit_view(self):
        return ReviewedCommitView.as_view(site=self)

    @cached_property
    def approve_view(self):
        return ApproveView.as_view(site=self)

    @cached_property
    def unapprove_view(self):
        return UnapproveView.as_view(site=self)

    @cached_property
    def undo_approvals_view(self):
        return UndoApprovalsView.as_view(site=self)

    @cached_property
    def history_view(self):
        return HistoryView.as_view(
            site=self, template_name='review_queue/history.html')
