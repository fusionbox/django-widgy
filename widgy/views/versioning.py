import tempfile
import subprocess

from django import forms
from django.views.generic import (
    FormView,
    DetailView,
    TemplateView,
)
from django.views.generic.detail import SingleObjectMixin
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.contrib.admin.widgets import AdminSplitDateTime
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.utils.encoding import force_text
from django.core.exceptions import PermissionDenied
from django.core import urlresolvers
from django.http import Http404

from bs4 import BeautifulSoup

from widgy.views.base import AuthorizedMixin
from widgy.utils import build_url

DIFF_ENABLED = bool(getattr(settings, 'DAISYDIFF_JAR_PATH', False))


class CommitForm(forms.Form):
    PUBLISH_RADIO_CHOICES = (
        ('now', _('Immediately')),
        ('later', _('Later')),
    )

    message = forms.CharField(widget=forms.Textarea,
                              label=_('Notes (optional)'),
                              required=False)
    publish_radio = forms.ChoiceField(label=_('Publish at'),
                                      widget=forms.RadioSelect,
                                      choices=PUBLISH_RADIO_CHOICES,
                                      initial=PUBLISH_RADIO_CHOICES[0][0],
                                      )
    publish_at = forms.SplitDateTimeField(initial=timezone.now,
                                          localize=True,
                                          required=False,
                                          widget=AdminSplitDateTime())

    def get_publish_at(self):
        if self.cleaned_data['publish_radio'] == 'now':
            publish_at = timezone.now()
        else:
            publish_at = self.cleaned_data['publish_at']
        return publish_at

    def commit(self, obj, user):
        return obj.commit(user,
                          message=self.cleaned_data['message'],
                          publish_at=self.get_publish_at())


class RevertForm(CommitForm):
    def commit(self, obj, user):
        return obj.tracker.revert_to(
            commit=obj,
            user=user,
            message=self.cleaned_data['message'],
            publish_at=self.get_publish_at(),
        )


class VersionTrackerMixin(SingleObjectMixin):
    def get_queryset(self):
        return self.site.get_version_tracker_model().objects.all().select_related(
            'head',
            'head__root_node',
            'working_copy')

    def get_preview_urls(self, root_node):
        for owner in self.object.owners:
            if hasattr(owner, 'get_action_links'):
                for link in owner.get_action_links(root_node):
                    if link['type'] == 'preview':
                        yield link

    def get_diff_urls(self, before_node, after_node):
        if DIFF_ENABLED:
            for a, b in zip(self.get_preview_urls(before_node), self.get_preview_urls(after_node)):
                yield build_url(self.site.reverse(self.site.diff_view),
                                before=a['url'],
                                after=b['url'])


class PopupView(object):
    def get_context_data(self, **kwargs):
        kwargs['is_popup'] = True
        kwargs['request'] = self.request
        return super(PopupView, self).get_context_data(**kwargs)


class CommitView(PopupView, AuthorizedMixin, VersionTrackerMixin, FormView):
    template_name = 'widgy/commit.html'
    form_class = CommitForm
    permission_error_message = _("You don't have permission to commit.")

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        kwargs = super(CommitView, self).get_context_data(**kwargs)
        kwargs['title'] = _('Commit Changes')
        kwargs['tracker'] = self.object
        kwargs['site'] = self.site
        kwargs['commit_url'] = self.site.reverse(self.site.commit_view,
                                                 kwargs={'pk': self.object.pk})
        if not self.has_permission(self.object):
            kwargs['permission_error_message'] = self.permission_error_message

        if self.object.head:
            kwargs['diff_urls'] = self.get_diff_urls(self.object.working_copy,
                                                     self.object.head.root_node)

        # lazy because the template doesn't always use it
        kwargs['changed_anything'] = lambda: self.object.has_changes()

        return kwargs

    def has_permission(self, obj):
        return self.site.has_add_permission(self.request, obj, obj.commit_model)

    def form_valid(self, form):
        obj = self.get_object()

        if not self.has_permission(obj):
            raise PermissionDenied(self.permission_error_message)

        form.commit(obj, self.request.user)
        # because this is a popup, we shouldn't redirect.
        return self.response_class(
            request=self.request,
            template='widgy/commit_success.html',
            context=self.get_context_data(),
        )


class ResetView(PopupView, AuthorizedMixin, VersionTrackerMixin, TemplateView):
    template_name = 'widgy/reset.html'
    permission_error_message = _("You don't have permission to reset.")

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        kwargs = super(ResetView, self).get_context_data(**kwargs)
        kwargs['title'] = _('Reset')
        kwargs['tracker'] = self.object
        kwargs['changed_anything'] = self.object.has_changes()
        kwargs['has_commits'] = bool(self.object.head)
        kwargs['reset_url'] = self.request.get_full_path()

        if not self.has_permission(self.object):
            kwargs['permission_error_message'] = self.permission_error_message

        return kwargs

    def has_permission(self, obj):
        # We don't really add a commit while resetting, but this permission is
        # used for everything commit related.
        return self.site.has_add_permission(self.request, obj, obj.commit_model)

    def post(self, request, *args, **kwargs):
        version_tracker = self.get_object()

        if not self.has_permission(version_tracker):
            raise PermissionDenied(self.permission_error_message)

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
        for commit in kwargs['commits']:
            if commit.parent_id:
                commit.diff_urls = self.get_diff_urls(commit.root_node, commit.parent.root_node)
        return kwargs


class RevertView(PopupView, AuthorizedMixin, VersionTrackerMixin, FormView):
    template_name = 'widgy/revert.html'
    pk_url_kwarg = 'commit_pk'
    form_class = RevertForm
    permission_error_message = _("You don't have permission to revert.")

    # get_object is in post and get because it needs to be called after the
    # authorization in dispatch. Putting it in RevertView's dispatch would
    # mean it gets called too early.

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(RevertView, self).post(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(RevertView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs = super(RevertView, self).get_context_data(**kwargs)
        kwargs['title'] = _('Revert Commit')
        kwargs['commit'] = self.object
        kwargs['tracker'] = self.object.tracker
        kwargs['site'] = self.site
        kwargs['revert_url'] = self.site.reverse(
            self.site.revert_view,
            kwargs={'pk': self.object.tracker.pk, 'commit_pk': self.object.pk})

        if not self.has_permission(self.object):
            kwargs['permission_error_message'] = self.permission_error_message

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
        kwargs = super(RevertView, self).get_form_kwargs()
        kwargs['initial'] = {
            'message': _('Revert to version %(version)s') % {'version': self.object},
        }
        return kwargs

    def has_permission(self, obj):
        parent = obj.tracker
        return self.site.has_add_permission(self.request, parent, type(obj))

    def form_valid(self, form):
        commit = self.object

        if not self.has_permission(commit):
            raise PermissionDenied(self.permission_error_message)

        form.commit(commit, user=self.request.user)

        return self.response_class(
            request=self.request,
            template='widgy/commit_success.html',
            context=self.get_context_data(),
        )


class DiffView(AuthorizedMixin, TemplateView):
    template_name = 'widgy/diff.html'

    def call_view_from_url(self, url):
        view, args, kwargs = urlresolvers.resolve(url)
        return view(self.request, *args, **kwargs).rendered_content

    def get_context_data(self, **kwargs):
        kwargs = super(DiffView, self).get_context_data(**kwargs)
        try:
            before_url = self.request.GET['before']
            after_url = self.request.GET['after']
        except KeyError:
            raise Http404

        before = self.call_view_from_url(before_url)
        after = self.call_view_from_url(after_url)

        kwargs['diff'] = daisydiff(before, after)

        return kwargs


def daisydiff(before, after):
    """
    Given two strings of html documents in a and b, return a string containing
    html representing the diff between a and b. Requires java and daisydiff.
    """
    with tempfile.NamedTemporaryFile() as f_a:
        with tempfile.NamedTemporaryFile() as f_b:
            with tempfile.NamedTemporaryFile() as f_out:
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
                for i in body.find_all(recursive=False)[:6]:
                    i.extract()
                return force_text(body)
