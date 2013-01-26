from django import forms
from django.views.generic import FormView, DetailView
from django.views.generic.detail import SingleObjectMixin
from widgy.views.base import WidgyViewMixin

class CommitForm(forms.Form):
    pass

class CommitView(WidgyViewMixin, SingleObjectMixin, FormView):
    template_name = 'widgy/commit.html'
    form_class = CommitForm

    def get_queryset(self):
        return self.site.get_version_tracker_model().objects.all()

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        kwargs = super(CommitView, self).get_context_data(**kwargs)
        kwargs['object'] = self.object
        kwargs['commit_url'] = self.site.reverse(self.site.commit_view, kwargs={'pk': self.object.pk})
        return kwargs

    def form_valid(self, form):
        object = self.get_object()
        object.commit(user=self.request.user)
        return self.response_class(
            request=self.request,
            template='widgy/commit_success.html',
            context=self.get_context_data(),
        )

class HistoryView(WidgyViewMixin, DetailView):
    template_name = 'widgy/history.html'

    def get_queryset(self):
        return self.site.get_version_tracker_model().objects.all()

    def get_context_data(self, **kwargs):
        kwargs = super(HistoryView, self).get_context_data(**kwargs)
        kwargs['commits'] = self.object.get_history()
        return kwargs
