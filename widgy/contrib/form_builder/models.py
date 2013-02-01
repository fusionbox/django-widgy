from django.db import models
from django import forms
from django.utils.datastructures import SortedDict
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.conf import settings

from widgy.models import Content
from widgy.models.mixins import DefaultChildrenMixin
from widgy.utils import update_context
from widgy.contrib.page_builder.db.fields import MarkdownField
import widgy


class FormElement(Content):
    editable = True

    class Meta:
        abstract = True

    @property
    def parent_form(self):
        for i in self.get_ancestors():
            if isinstance(i, Form):
                return i

        assert False, "This FormElement, doesn't belong to a Form?!?!?"

    @classmethod
    def valid_child_of(cls, parent, obj=None):
        for p in list(parent.get_ancestors()) + [parent]:
            if isinstance(p, Form):
                return super(FormElement, cls).valid_child_of(parent, obj)
        return False


class FormSuccessHandler(Content):
    editable = True

    class Meta:
        abstract = True

    @classmethod
    def valid_child_of(cls, parent, obj=None):
        return isinstance(parent, SubmitButton)


class FormReponseHandler(FormSuccessHandler):
    class Meta:
        abstract = True


@widgy.register
class EmailSuccessHandler(FormSuccessHandler):
    to = models.EmailField()
    content = MarkdownField(blank=True)

    component_name = 'markdown'

    def execute(self, request, form):
        send_mail('Subject', self.content, settings.SERVER_EMAIL, [self.to])


@widgy.register
class SubmitButton(FormElement):
    text = models.CharField(max_length=255, default='submit')

    @property
    def deletable(self):
        return len([i for i in self.parent_form.depth_first_order() if isinstance(i, SubmitButton)]) > 1

    def valid_parent_of(self, cls, obj=None):
        if obj in self.get_children():
            return True

        # only accept one FormReponseHandler
        if issubclass(cls, FormReponseHandler) and any([isinstance(child, FormReponseHandler)
                                                        for child in self.get_children()]):
            return False

        return issubclass(cls, FormSuccessHandler)


@widgy.register
class Form(DefaultChildrenMixin, Content):
    accepting_children = True
    shelf = True

    default_children = [
        (SubmitButton, (), {}),
    ]

    @property
    def action_url(self):
        return reverse('widgy.contrib.widgy_mezzanine.views.handle_form',
                       kwargs={
                           'node_pk': self.node.pk,
                       })

    def valid_parent_of(self, cls, obj=None):
        return True

    @classmethod
    def valid_child_of(cls, parent, obj=None):
        for p in list(parent.get_ancestors()) + [parent]:
            if isinstance(p, Form):
                return False
        return super(Form, cls).valid_child_of(parent, obj)

    def get_form(self):
        fields = SortedDict((child.get_formfield_name(), child.get_formfield())
                            for child in self.get_children() if isinstance(child, FormField))

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

    def execute(self, request, form):
        # TODO: only call the handlers for the submit button that was pressed.
        resp = None
        for child in self.depth_first_order():
            if isinstance(child, FormReponseHandler):
                resp = child.execute(request, form)
            elif isinstance(child, FormSuccessHandler):
                child.execute(request, form)
        return resp


class FormField(FormElement):
    formfield_class = None
    widget = None

    label = models.CharField(max_length=255)

    help_text = models.TextField(blank=True)

    class Meta:
        abstract = True

    def get_formfield_name(self):
        return str(self.node.pk)

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


@widgy.register
class FormInput(FormField):
    formfield_class = forms.CharField
    form = FormInputForm

    type = models.CharField(choices=FORM_INPUT_TYPES, max_length=255)


@widgy.register
class Textarea(FormField):
    formfield_class = forms.CharField
    widget = forms.Textarea
