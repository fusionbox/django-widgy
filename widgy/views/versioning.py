import tempfile
import subprocess
import contextlib

from django import forms
from django.views.generic import (
    FormView,
    DetailView,
    TemplateView,
    RedirectView,
)
from django.views.generic.detail import SingleObjectMixin
from django.shortcuts import get_object_or_404, redirect
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.contrib import messages

from BeautifulSoup import BeautifulSoup

from widgy.views.base import AuthorizedMixin
from widgy.models import Node

DIFF_ENABLED = bool(getattr(settings, 'DAISYDIFF_JAR_PATH', False))


def diff_url(site, before, after):
    if DIFF_ENABLED:
        return site.reverse(site.diff_view, kwargs={
            'before_pk': before.pk,
            'after_pk': after.pk,
        })
    else:
        return None


class CommitForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea,
                              label=_('Notes (optional)'),
                              required=False)
    publish_at = forms.DateTimeField(required=True,
                                     initial=timezone.now)

    def commit(self, obj, user):
        obj.commit(user, **self.cleaned_data)


class ReviewedCommitForm(CommitForm):
    approve_it = forms.BooleanField(label=_('Approve the commit'),
                                     required=False)

    def commit(self, obj, user):
        cleaned_data = self.cleaned_data.copy()
        approve_it = cleaned_data.pop('approve_it')

        commit = obj.commit(user, **cleaned_data)

        if approve_it:
            commit.approve(user)


class RevertForm(CommitForm):
    pass


class VersionTrackerMixin(SingleObjectMixin):
    def get_queryset(self):
        return self.site.get_version_tracker_model().objects.all().select_related(
            'head',
            'head__root_node',
            'working_copy')


class CommitView(AuthorizedMixin, VersionTrackerMixin, FormView):
    template_name = 'widgy/commit.html'
    form_class = CommitForm

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        kwargs = super(CommitView, self).get_context_data(**kwargs)
        kwargs['object'] = self.object
        kwargs['commit_url'] = self.site.reverse(self.site.commit_view,
                                                 kwargs={'pk': self.object.pk})
        if self.object.head:
            kwargs['diff_url'] = diff_url(self.site,
                                          self.object.working_copy,
                                          self.object.head.root_node)

        # lazy because the template doesn't always use it
        kwargs['changed_anything'] = lambda: self.object.has_changes()

        return kwargs

    def form_valid(self, form):
        obj = self.get_object()
        form.commit(obj, self.request.user)
        return self.response_class(
            request=self.request,
            template='widgy/commit_success.html',
            context=self.get_context_data(),
        )

    def get_form_class(self):
        return self.site.get_commit_form(self.request.user)


class ResetView(AuthorizedMixin, VersionTrackerMixin, TemplateView):
    template_name = 'widgy/reset.html'

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        kwargs = super(ResetView, self).get_context_data(**kwargs)
        kwargs['object'] = self.object
        kwargs['changed_anything'] = self.object.has_changes()
        kwargs['has_commits'] = bool(self.object.head)
        kwargs['reset_url'] = self.request.get_full_path()
        return kwargs

    def post(self, request, *args, **kwargs):
        version_tracker = self.get_object()
        version_tracker.reset()
        return self.response_class(
            request=self.request,
            template='widgy/reset_success.html',
            context=self.get_context_data(),
        )


class HistoryView(AuthorizedMixin, VersionTrackerMixin, DetailView):
    template_name = 'widgy/history.html'

    def get_context_data(self, **kwargs):
        kwargs = super(HistoryView, self).get_context_data(**kwargs)
        kwargs['site'] = self.site
        kwargs['commits'] = self.object.get_history_list()
        kwargs['history_item_template'] = self.site.get_version_tracker_model().item_partial_template
        for commit in kwargs['commits']:
            if commit.parent_id:
                commit.diff_url = diff_url(self.site,
                                           commit.parent.root_node,
                                           commit.root_node)
        return kwargs


class ReviewedHistoryView(HistoryView):

    def get_context_data(self, **kwargs):
        kwargs = super(ReviewedHistoryView, self).get_context_data(**kwargs)
        try:
            self.site.authorize(self.request, self.site.approve_view.view_instance)
            kwargs['can_approve_commit'] = True
        except PermissionDenied:
            kwargs['can_approve_commit'] = False
        return kwargs


class ApproveView(AuthorizedMixin, VersionTrackerMixin, RedirectView):
    http_method_names = ['post']

    def get_redirect_url(self, pk, commit_pk):
        vt = get_object_or_404(self.get_queryset(), pk=pk)
        commit = get_object_or_404(vt.commits.select_related('root_node'),
                                   pk=commit_pk)
        commit.tracker = vt

        commit.approve(self.request.user)
        commit.save()
        messages.success(self.request, _('Commit has been approved'))

        return self.site.reverse(self.site.history_view, kwargs={
            'pk': vt.pk
        })



class RevertView(AuthorizedMixin, VersionTrackerMixin, FormView):
    template_name = 'widgy/revert.html'
    pk_url_kwarg = 'commit_pk'
    form_class = RevertForm

    def get_context_data(self, **kwargs):
        kwargs['object'] = self.object
        kwargs = super(RevertView, self).get_context_data(**kwargs)
        kwargs['revert_url'] = self.site.reverse(
            self.site.revert_view,
            kwargs={'pk': self.object.tracker.pk, 'commit_pk': self.object.pk})
        return kwargs

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        vt = get_object_or_404(queryset, pk=self.kwargs['pk'])
        commit = get_object_or_404(vt.commits.select_related('root_node'),
                                   pk=self.kwargs['commit_pk'])
        commit.tracker = vt
        return commit

    def get_form_kwargs(self):
        self.object = self.get_object()
        kwargs = super(RevertView, self).get_form_kwargs()
        kwargs['initial'] = {
            'message': _('Revert to version %(version)s') % {'version': self.object},
        }
        return kwargs

    def form_valid(self, form):
        commit = self.get_object()
        commit.tracker.revert_to(commit, user=self.request.user, **form.cleaned_data)

        return self.response_class(
            request=self.request,
            template='widgy/commit_success.html',
            context=self.get_context_data(),
        )


class DiffView(AuthorizedMixin, TemplateView):
    template_name = 'widgy/diff.html'

    def get_context_data(self, **kwargs):
        from widgy.contrib.widgy_mezzanine.views import preview

        kwargs = super(DiffView, self).get_context_data(**kwargs)

        before_node = get_object_or_404(Node, pk=self.kwargs['before_pk'])
        after_node = get_object_or_404(Node, pk=self.kwargs['after_pk'])
        Node.prefetch_trees(before_node, after_node)
        a = preview(self.request, before_node.pk, node=before_node)
        b = preview(self.request, after_node.pk, node=after_node)

        kwargs['diff'] = daisydiff(a.rendered_content, b.rendered_content)

        return kwargs


class UndoApprovalsView(AuthorizedMixin, FormView):
    http_method_names = ['post']

    def get_form_class(self):
        # XXX: Avoid circular import
        from widgy.forms import UndoApprovalsForm
        return UndoApprovalsForm

    def form_valid(self, form):
        # XXX: Avoid circular import
        from widgy.models import VersionCommit
        approved_commits = form.cleaned_data['actions']
        if not isinstance(approved_commits, list) or \
           not all([isinstance(i, int) for i in approved_commits]):
            return self.form_invalid()

        commits = VersionCommit.objects.filter(pk__in=approved_commits)
        for c in commits:
            c.unapprove(self.request.user)
        return redirect(form.cleaned_data['referer'])

    def form_invalid(self, form):
        return redirect('/')


def daisydiff(before, after):
    """
    Given two strings of html documents in a and b, return a string containing
    html representing the diff between a and b. Requires java and daisydiff.
    """
    files = [tempfile.NamedTemporaryFile() for i in range(3)]
    with contextlib.nested(*files) as (f_a, f_b, f_out):
        f_a.write(before.encode('utf-8'))
        f_b.write(after.encode('utf-8'))

        f_a.flush()
        f_b.flush()

        proc = subprocess.Popen(stdout=subprocess.PIPE, args=[
            'java',
            '-jar',
            settings.DAISYDIFF_JAR_PATH,
            f_b.name,
            f_a.name,
            '--file=' + f_out.name,
        ])
        proc.communicate()
        retcode = proc.poll()
        if retcode:
            assert False, "Daisydiff returned %s" % retcode

        diff_html = f_out.read().decode('utf-8')

        # remove the daisydiff chrome so we can add our own
        parsed = BeautifulSoup(diff_html)
        body = parsed.find('body')
        for i in body.findAll(recursive=False)[:6]:
            i.extract()
        return unicode(body)
