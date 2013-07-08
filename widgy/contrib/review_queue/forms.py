import json

from django import forms
from django.template import RequestContext
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string

from widgy.models import VersionCommit
from widgy.views.versioning import CommitForm


class JsonField(forms.CharField):
    def to_python(self, value):
        try:
            result = json.loads(value)
            return result
        except ValueError:
            raise forms.ValidationError

    def prepare_value(self, value):
        return json.dumps(value)


class UndoApprovalsForm(forms.Form):
    actions = JsonField(widget=forms.HiddenInput, required=True)
    referer = forms.CharField(widget=forms.HiddenInput, required=True)

    def render(self, request, site):
        return mark_safe(
            render_to_string(
                'review_queue/undoform.html',
                {
                    'form': self,
                    'site': site,
                },
                RequestContext(request),
            )
        )


class ApproveForm(forms.ModelForm):
    approve = forms.BooleanField(required=False)

    class Meta:
        model = VersionCommit
        fields = ('publish_at', )

    def save(self, request, commit=True):
        if self.cleaned_data['approve']:
            self.instance.approve(request.user, commit=commit)
        return super(ApproveForm, self).save(commit=commit)


class ReviewedCommitForm(CommitForm):
    def commit(self, obj, user):
        approve_it = 'approve_it' in self.data

        commit = super(ReviewedCommitForm, self).commit(obj, user)

        if approve_it:
            commit.reviewedversioncommit.approve(user)
