from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from widgy.utils import format_html
from django.views.generic import RedirectView, FormView
from django.core.exceptions import PermissionDenied

from widgy.views.base import AuthorizedMixin
from widgy.views.versioning import VersionTrackerMixin, CommitForm, CommitView

from .forms import UndoApprovalsForm
from .models import ReviewedVersionCommit


class ReviewedCommitForm(CommitForm):
    def commit(self, obj, user):
        cleaned_data = self.cleaned_data.copy()
        approve_it = 'approve_it' in self.data

        commit = obj.commit(user, **cleaned_data)

        if approve_it:
            commit.reviewedversioncommit.approve(user)


class ReviewedCommitView(CommitView):
    template_name = 'review_queue/commit.html'

    def get_form_class(self):
        try:
            self.site.authorize(
                self.request,
                self.site.get_view_instance(self.site.approve_view),
            )
            return ReviewedCommitForm
        except PermissionDenied:
            return super(ReviewedCommitView, self).get_form_class()


class ApprovalChangeBaseView(AuthorizedMixin, VersionTrackerMixin, RedirectView):
    """
    Abstract class for approving or unapproving commits
    """
    http_method_names = ['post']

    def get_redirect_url(self, pk, commit_pk):
        vt = get_object_or_404(self.get_queryset(), pk=pk)
        commit = get_object_or_404(vt.commits.select_related('root_node'),
                                   pk=commit_pk)
        commit.tracker = vt

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
        # XXX: Avoid circular import
        from .admin import HTML_IN_MESSAGES

        message = _('Commit %s has been approved') % commit
        if HTML_IN_MESSAGES:
            message = format_html('{0} {1}',
                message,
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
        return _('Commit %s has been unapproved') % commit


class UndoApprovalsView(AuthorizedMixin, FormView):
    http_method_names = ['post']

    def get_form_class(self):
        return UndoApprovalsForm

    def form_valid(self, form):
        approved_commits = form.cleaned_data['actions']
        if not isinstance(approved_commits, list) or \
           not all([isinstance(i, int) for i in approved_commits]):
            return self.form_invalid()

        commits = ReviewedVersionCommit.objects.filter(pk__in=approved_commits)
        for c in commits:
            c.unapprove(self.request.user)
        return redirect(form.cleaned_data['referer'])

    def form_invalid(self, form):
        return redirect('/')
