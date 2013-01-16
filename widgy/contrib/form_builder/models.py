from django.db import models
from django import forms
from django.utils.datastructures import SortedDict
from django.core.urlresolvers import reverse

from widgy.models import Content
from widgy.utils import update_context
from widgy.contrib.page_builder.models import Widget
from widgy import registry


class Form(Content):
    accepting_children = True
    shelf = True
    component_name = 'bucket'

    @property
    def action_url(self):
        return reverse('widgy.contrib.widgy_mezzanine.views.handle_form',
                       kwargs={
                           'node_pk': self.node.pk,
                       })

    @classmethod
    def valid_child_of(cls, parent, obj=None):
        for p in list(parent.get_ancestors()) + [parent]:
            if isinstance(p, Form):
                return False
        return super(Form, cls).valid_child_of(parent, obj)

    def get_form(self):
        fields = SortedDict((child.get_formfield_name(), child.get_formfield())
                            for child in self.children if isinstance(child, FormField))

        return type('WidgyForm', (forms.BaseForm,), {'base_fields': fields})

    @property
    def context_var(self):
        return 'form_instance_{node_pk}'.format(node_pk=self.node.pk)

    def render(self, context):
        if self.context_var in context:
            form = context[self.context_var]
        else:
            form = self.get_form()()

        with update_context(context, {'form': form}):
            return super(Form, self).render(context)


registry.register(Form)


class FormField(FormElement):
    formfield_class = None
    widget = None

    label = models.CharField(max_length=255)

    help_text = models.TextField(blank=True)

    class Meta:
        abstract = True

    def get_formfield_name(self):
        return str(self.id)

    def get_formfield(self):
        kwargs = {
            'label': self.label,
            'help_text': self.help_text,
            'widget': self.widget,
        }

        return self.formfield_class(**kwargs)

    def render(self, context):
        form = context['form']
        field = form[self.get_formfield_name()]
        with update_context(context, {'field': field}):
            return super(FormField, self).render(context)


FORM_INPUT_TYPES = (
    ('text', 'Text'),
    ('number', 'Number'),
)


class FormInputForm(forms.ModelForm):
    class Meta:
        fields = (
            'type',
            'label',
            'help_text',
        )
#
#    def clean(self):
#        raise forms.ValidationError('asdfasd')


class FormInput(FormField):
    formfield_class = forms.CharField
    form = FormInputForm

    type = models.CharField(choices=FORM_INPUT_TYPES, max_length=255)

registry.register(FormInput)


class Textarea(FormField):
    formfield_class = forms.CharField
    widget = forms.Textarea

registry.register(Textarea)


class SubmitButton(FormElement):
    text = models.CharField(max_length=255, default='submit')

registry.register(SubmitButton)
