from django.db import models
from django import forms
from django.core.exceptions import ImproperlyConfigured
from django.utils.datastructures import SortedDict

from widgy.models import Content
from widgy.contrib.page_builder.models import Widget
from widgy import registry


class Form(Content):
    accepting_children = True
    #shelf = True
    component_name = 'bucket'

    @classmethod
    def valid_child_of(cls, parent, obj=None):
        for parent in list(parent.get_ancestors()) + [parent]:
            if isinstance(parent, Form):
                return False
        return super(Form, cls).valid_child_of(parent, obj)

    def get_form(self):
        fields = SortedDict((child.get_formfield_name(), child.get_formfield())
                            for child in self.children if isinstance(child, FormField))

        return type('WidgyForm', (forms.BaseForm,), {'base_fields': fields})


registry.register(Form)


class FormElement(Widget):
    editable = True

    class Meta:
        abstract = True

    @classmethod
    def valid_child_of(cls, parent, obj=None):
        for parent in list(parent.get_ancestors()) + [parent]:
            if isinstance(parent, Form):
                return super(FormElement, cls).valid_child_of(parent, obj)
        return False


class FormField(FormElement):
    formfield_class = None

    label = models.CharField(max_length=255)

    help_text = models.TextField(blank=True)

    class Meta:
        abstract = True

    def get_formfield_name(self):
        return str(self.id)

    def get_formfield(self):
        return self.formfield_class(label=self.label, help_text=self.help_text)


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
    pass

registry.register(Textarea)


class SubmitButton(FormElement):
    text = models.CharField(max_length=255, default='submit')

registry.register(SubmitButton)
