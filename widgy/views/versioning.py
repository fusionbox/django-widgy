from django import forms
from django.views.generic import FormView, DetailView
from django.views.generic.detail import SingleObjectMixin
from django.shortcuts import get_object_or_404
from widgy.views.base import WidgyViewMixin, AuthorizedMixin


class CommitForm(forms.Form):
    pass


class RevertForm(forms.Form):
    pass


class VersionTrackerMixin(SingleObjectMixin):
    def get_queryset(self):
        return self.site.get_version_tracker_model().objects.all().select_related('head')


class CommitView(WidgyViewMixin, AuthorizedMixin, VersionTrackerMixin, FormView):
    template_name = 'widgy/commit.html'
    form_class = CommitForm

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        kwargs = super(CommitView, self).get_context_data(**kwargs)
        kwargs['object'] = self.object
        kwargs['commit_url'] = self.site.reverse(self.site.commit_view,
                                                 kwargs={'pk': self.object.pk})
        return kwargs

    def form_valid(self, form):
        object = self.get_object()
        object.commit(user=self.request.user)
        return self.response_class(
            request=self.request,
            template='widgy/commit_success.html',
            context=self.get_context_data(),
        )


class HistoryView(WidgyViewMixin, AuthorizedMixin, VersionTrackerMixin, DetailView):
    template_name = 'widgy/history.html'

    def get_queryset(self):
        return super(HistoryView, self).get_queryset().select_related('head__root_node')

    def get_context_data(self, **kwargs):
        kwargs = super(HistoryView, self).get_context_data(**kwargs)
        kwargs['commits'] = self.object.get_history_list()
        for commit in kwargs['commits']:
            if commit.root_node != commit.tracker.head.root_node:
                commit.revert_url = self.site.reverse(
                    self.site.revert_view,
                    kwargs={'pk': commit.tracker.pk, 'commit_pk': commit.pk})
        return kwargs


class RevertView(WidgyViewMixin, AuthorizedMixin, VersionTrackerMixin, FormView):
    template_name = 'widgy/revert.html'
    pk_url_kwarg = 'commit_pk'
    form_class = RevertForm

    def get_context_data(self, **kwargs):
        self.object = kwargs['object'] = self.get_object()
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

    def form_valid(self, form):
        commit = self.get_object()
        commit.tracker.revert_to(commit, user=self.request.user)

        return self.response_class(
            request=self.request,
            template='widgy/commit_success.html',
            context=self.get_context_data(),
        )
