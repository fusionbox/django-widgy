from __future__ import unicode_literals

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.utils.http import is_safe_url
from django.utils.html import format_html
from django.views.generic import RedirectView, FormView
from django.core.exceptions import PermissionDenied

from widgy.views.base import AuthorizedMixin
from widgy.views.versioning import VersionTrackerMixin, CommitView, HistoryView as OldHistoryView

from .forms import UndoApprovalsForm, ReviewedCommitForm
from .models import ReviewedVersionCommit


class ReviewedCommitView(CommitView):
    template_name = 'review_queue/commit.html'

    def get_form_class(self):
        if self.site.has_change_permission(self.request, ReviewedVersionCommit):
            return ReviewedCommitForm
        else:
            return super(ReviewedCommitView, self).get_form_class()


class ApprovalChangeBaseView(AuthorizedMixin, VersionTrackerMixin, RedirectView):
    """
    Abstract class for approving or unapproving commits
    """
    http_method_names = ['post']
    permanent = False

    def get_redirect_url(self, pk, commit_pk):
        vt = get_object_or_404(self.get_queryset(), pk=pk)
        commit = get_object_or_404(vt.commits.select_related('root_node'),
                                   pk=commit_pk)
        commit.tracker = vt

        if not self.site.has_change_permission(self.request, commit.reviewedversioncommit):
            raise PermissionDenied(_("You don't have permission to approve commits."))

        self.action(commit)

        history_url = self.site.reverse(self.site.history_view, kwargs={
            'pk': vt.pk
        })

        messages.success(self.request, self.get_message(commit, history_url))

        return history_url

    def action(self, commit):
        raise NotImplementedError("action should be implemented in subclass")

    def get_message(self, commit, history_url):
        raise NotImplementedError("get_message should be implemented in subclass")


class ApproveView(ApprovalChangeBaseView):
    def action(self, commit):
        commit.reviewedversioncommit.approve(self.request.user)
        commit.save()

    def get_message(self, commit, history_url):
        message = format_html('{0} {1}',
            _('Commit %s has been approved') % commit,
            UndoApprovalsForm(
                initial={
                    'actions': [commit.pk],
                    'referer': history_url,
                }
            ).render(self.request, self.site)
        )
        return message


class UnapproveView(ApprovalChangeBaseView):
    def action(self, commit):
        commit.reviewedversioncommit.unapprove(self.request.user)
        commit.save()

    def get_message(self, commit, history_url):
        return _('Commit %s has been unapproved.') % commit


class UndoApprovalsView(AuthorizedMixin, FormView):
    http_method_names = ['post']
    form_class = UndoApprovalsForm

    def form_valid(self, form):
        approved_commits = form.cleaned_data['actions']
        if not isinstance(approved_commits, list) or \
           not all(isinstance(i, int) for i in approved_commits):
            return self.form_invalid()

        commits = ReviewedVersionCommit.objects.filter(pk__in=approved_commits)

        if not all(self.site.has_change_permission(self.request, c) for c in commits):
            raise PermissionDenied(_("You don't have permission to approve commits."))

        for c in commits:
            c.unapprove(self.request.user)
        url = form.cleaned_data['referer']
        if not is_safe_url(url=url, host=self.request.get_host()):
            url = '/'
        return redirect(url)

    def form_invalid(self, form):
        return redirect('/')


class HistoryView(OldHistoryView):
    def get_context_data(self, **kwargs):
        kwargs = super(HistoryView, self).get_context_data(**kwargs)
        # it's not useful to approve/unapprove commits past the latest approved
        # commit
        interesting = True
        for commit in kwargs['commits']:
            commit.is_interesting_to_approve_or_unapprove = interesting
            interesting &= not self.object.commit_is_ready(commit)
        return kwargs
