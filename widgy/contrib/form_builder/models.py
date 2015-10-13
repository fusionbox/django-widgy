from __future__ import unicode_literals

import csv
import urllib
import base64
import hashlib
import os.path
import six
from collections import OrderedDict

from django.db import models
from django import forms
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.utils.translation import ugettext_lazy as _, ugettext
from django.shortcuts import redirect
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils.functional import cached_property
from django.utils.encoding import python_2_unicode_compatible, force_bytes, force_text
from django.template.defaultfilters import truncatechars
from django.core.files import File
from django.core.files.storage import default_storage

from django_extensions.db.fields import UUIDField
import html2text

from widgy.models import Content, Node
from widgy.signals import pre_delete_widget
from widgy.models.mixins import StrictDefaultChildrenMixin, DefaultChildrenMixin, TabbedContainer, StrDisplayNameMixin
from widgy.utils import update_context, build_url, QuerySet
from widgy.contrib.page_builder.models import Bucket, Html
from widgy.contrib.page_builder.forms import MiniCKEditorField, CKEditorField
from .forms import PhoneNumberField
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
            if isinstance(p, FormBody):
                return super(FormElement, cls).valid_child_of(parent, obj)
        return False


class FormSuccessHandler(FormElement):
    draggable = True

    class Meta:
        abstract = True

    @classmethod
    def valid_child_of(cls, parent, obj=None):
        return isinstance(parent, SuccessHandlers)


class FormReponseHandler(FormSuccessHandler):
    class Meta:
        abstract = True


@widgy.register
class SaveDataHandler(FormSuccessHandler):
    editable = False
    tooltip = _("Saves the data when the Form is filled out. This is enabled by"
                " default.")

    class Meta:
        verbose_name = _('save data handler')
        verbose_name_plural = _('save data handlers')

    def execute(self, request, form):
        FormSubmission.objects.submit(
            form=self.parent_form,
            data=form.cleaned_data
        )


class BaseMappingHandler(FormSuccessHandler):
    """
    Abstract class for easily creating a form mapper.

    Inherit from this class if you want to create a mapper which
    upload the form data to a FTP server for example.
    """

    class Meta:
        abstract = True

    def get_mapping(self, request, form):
        mapping = dict()
        for child in self.get_children():
            child.update_mapping(mapping, form)
        return mapping


class RepostHandler(BaseMappingHandler):
    """
    Abstract class for easily creating a mapper that repost data
    to another form.

    The subclass must have a url_to_post field.
    """

    class Meta:
        abstract = True

    def execute(self, request, form):
        query_string = urllib.urlencode(self.get_mapping(request, form))
        urllib.urlopen(self.url_to_post, query_string)


class MappingValue(FormElement):
    """
    Abstract class for creating a mapping value.

    Inherit from this class if you want to create a ConstantMappingValue
    for example.

    You need to implement update_mapping(self, mapping, form) in subclasses.
    """
    class Meta:
        abstract = True

    @classmethod
    def valid_child_of(cls, parent, obj=None):
        return isinstance(parent, BaseMappingHandler)


class FieldMappingValueForm(forms.ModelForm):
    field_ident = forms.ChoiceField(label=_('Field'), choices=[])

    def __init__(self, *args, **kwargs):
        super(FieldMappingValueForm, self).__init__(*args, **kwargs)
        self.fields['field_ident'].choices = [('', _('------'))] + [
            (str(i.ident), i) for i in self.instance.get_fields()
        ]


@widgy.register
@python_2_unicode_compatible
class FieldMappingValue(StrDisplayNameMixin, MappingValue):
    """
    MappingValue that maps a form field to another value.
    """
    form = FieldMappingValueForm
    name = models.CharField(max_length=255)

    field_ident = models.CharField(max_length=36)

    class Meta:
        verbose_name = _('mapped field')
        verbose_name_plural = _('mapped field')

    def __str__(self):
        try:
            label = self.fields_mapping[self.field_ident].label
        except KeyError:
            return u''
        else:
            return _('{0} to {1}').format(label, self.name)

    def get_fields(self):
        return [f for f in self.parent_form.depth_first_order()
                if isinstance(f, FormField)]

    def update_mapping(self, mapping, form):
        try:
            form_field_name = self.fields_mapping[self.field_ident].get_formfield_name()
            mapping[self.name] = form.cleaned_data[form_field_name]
        except KeyError:
            pass

    @cached_property
    def fields_mapping(self):
        # Dict comprehension syntax for Python <2.7
        return dict(
            (field.ident, field)
            for field in self.parent_form.depth_first_order()
            if isinstance(field, FormField)
        )


@widgy.register
class WebToLeadMapperHandler(RepostHandler):
    """
    Mapper which repost form data to SalesForce
    """
    url_to_post = 'https://www.salesforce.com/servlet/servlet.WebToLead?encoding=UTF-8'
    oid = models.CharField(_('Organization ID (OID)'), max_length=16)

    class Meta:
        verbose_name = _('Salesforce Web-to-Lead')
        verbose_name_plural = _('Salesforce Web-to-Lead')

    def get_mapping(self, request, form):
        mapping = super(WebToLeadMapperHandler, self).get_mapping(request, form)
        mapping.update(oid=self.oid)
        return mapping

    def valid_parent_of(self, cls, obj=None):
        return issubclass(cls, FieldMappingValue)


class EmailSuccessHandlerBaseForm(forms.ModelForm):
    content = CKEditorField()


@python_2_unicode_compatible
class EmailSuccessHandlerBase(StrDisplayNameMixin, FormSuccessHandler):
    subject = models.CharField(max_length=255, verbose_name=_('subject'))
    content = models.TextField(blank=True, verbose_name=_('content'))
    include_form_data = models.BooleanField(
        verbose_name=_('include form data'),
        help_text=_("Should the form's data be included in the email?"),
        blank=True,
        default=False,
    )

    form = EmailSuccessHandlerBaseForm

    class Meta:
        abstract = True

    def __str__(self):
        return truncatechars(self.subject, 35)

    def format_message(self, request, form):
        data = []
        # keep the data in the same order as the form
        for name, field in self.parent_form.get_fields().items():
            serialized_value = field.serialize_value(
                form.cleaned_data[name]
            )
            data.append((field.label, serialized_value))
        return render_to_string('widgy/form_builder/form_email.html', {
            'data': data,
            'self': self,
        })

    def execute(self, request, form):
        message_text = self.format_message(request, form)
        msg = EmailMultiAlternatives(
            subject=self.subject,
            body=html2text.html2text(message_text),
            from_email=settings.SERVER_EMAIL,
            to=self.get_to_emails(form),
        )
        msg.attach_alternative(message_text, 'text/html')

        if self.include_form_data:
            for value in form.cleaned_data.values():
                if isinstance(value, File):
                    msg.attach(value.name, value.read(), getattr(value, 'content_type', None))

        msg.send()

    def get_to_emails(self, form):
        raise NotImplemented


@widgy.register
class EmailSuccessHandler(EmailSuccessHandlerBase):
    to = models.EmailField(verbose_name=_('to'))

    tooltip = _("This widget can be used to send yourself an email when a form"
                " has been filled out. You can customize the body of the"
                " email.")

    class Meta:
        verbose_name = _('admin success email')
        verbose_name_plural = _('admin success emails')

    def get_to_emails(self, form):
        if self.to:
            return [self.to]
        else:
            return []

# This is the only way to change a field provided by a base class.
EmailSuccessHandler._meta.get_field('include_form_data').default = True


class EmailUserHandlerForm(EmailSuccessHandlerBaseForm):
    to_ident = forms.ChoiceField(label=_('To'), choices=[])

    class Meta:
        fields = ('to_ident', 'subject', 'content', 'include_form_data')

    def __init__(self, *args, **kwargs):
        super(EmailUserHandlerForm, self).__init__(*args, **kwargs)
        self.fields['to_ident'].choices = [('', _('------'))] + [(i.ident, i) for i in self.instance.get_email_fields()]


@widgy.register
class EmailUserHandler(EmailSuccessHandlerBase):
    editable = True
    form = EmailUserHandlerForm
    tooltip = _("This widget can be used to send the user an email when they"
                " fill out a form. You can customize the body of the email.")

    # an input in our form
    to_ident = models.CharField(_('to'), max_length=36)

    class Meta:
        verbose_name = _('user success email')
        verbose_name_plural = _('user success emails')

    def get_to_emails(self, form):
        try:
            to = [f for f in self.parent_form.depth_first_order()
                  if hasattr(f, 'ident') and f.ident == self.to_ident][0]
        except IndexError:
            # no matching fields found, or to_ident is blank
            return []
        else:
            return [form.cleaned_data[to.get_formfield_name()]]

    def get_email_fields(self):
        return [i for i in self.parent_form.depth_first_order()
                if isinstance(i, FormInput) and i.type == 'email']

    def post_create(self, site):
        email_fields = self.get_email_fields()
        if email_fields:
            self.to_ident = email_fields[0].ident
        self.save()


@widgy.register
@python_2_unicode_compatible
class SubmitButton(StrDisplayNameMixin, FormElement):
    text = models.CharField(max_length=255, default=_('submit'), verbose_name=_('text'))

    tooltip = _("The submit button for a form.")

    @property
    def deletable(self):
        return len([i for i in self.parent_form.depth_first_order() if isinstance(i, SubmitButton)]) > 1

    class Meta:
        verbose_name = _('submit button')
        verbose_name_plural = _('submit buttons')

    def __str__(self):
        return self.text


def untitled_form():
    untitled = ugettext('Untitled form')
    n = Form.objects.filter(name__startswith=untitled + ' ').exclude(
        _nodes__is_frozen=True
    ).count() + 1
    return '%s %d' % (untitled, n)


class SuccessMessageBucket(DefaultChildrenMixin, Bucket):
    default_children = [
        (Html, (), {'content': 'Thank you.'}),
    ]

    class Meta:
        verbose_name = _('success message')
        verbose_name_plural = _('success messages')

    @classmethod
    def valid_child_of(cls, parent, obj=None):
        return isinstance(parent, FormMeta)


class SuccessHandlers(DefaultChildrenMixin, Bucket):
    default_children = [
        (SaveDataHandler, (), {}),
    ]

    class Meta:
        verbose_name = _('success handlers')
        verbose_name_plural = _('success handlers')

    def valid_parent_of(self, cls, obj=None):
        if obj in self.get_children():
            return True

        # only accept one FormReponseHandler
        if issubclass(cls, FormReponseHandler) and any([isinstance(child, FormReponseHandler)
                                                        for child in self.get_children()]):
            return False

        return issubclass(cls, FormSuccessHandler)

    @classmethod
    def valid_child_of(cls, parent, obj=None):
        return isinstance(parent, FormMeta)


class FormBody(DefaultChildrenMixin, Bucket):
    default_children = [
        (SubmitButton, (), {}),
    ]
    shelf = True

    class Meta:
        verbose_name = _('fields')
        verbose_name_plural = _('fields')

    @classmethod
    def valid_child_of(cls, parent, obj=None):
        return isinstance(parent, Form)


class FormMeta(StrictDefaultChildrenMixin, Bucket):
    default_children = [
        ('message', SuccessMessageBucket, (), {}),
        ('handlers', SuccessHandlers, (), {}),
    ]
    shelf = True

    class Meta:
        verbose_name = _('settings')
        verbose_name_plural = _('settings')

    @classmethod
    def valid_child_of(cls, parent, obj=None):
        return isinstance(parent, Form)


def friendly_uuid(uuid):
    """
    A shortend version of a UUID to use when collisions are acceptable.
    The returned string will have 40 bits of entropy assuming a UUID4.
    """
    result = base64.b32encode(hashlib.sha1(force_bytes(uuid)).digest()[:5]).lower()
    unicode_result = result.decode('ascii')
    # avoid accidental profanity
    profanity_filter = (unicode_result.replace('e', '0')
                                      .replace('o', '1')
                                      .replace('u', '8')
                                      .replace('i', '9'))
    return profanity_filter


@widgy.register
@python_2_unicode_compatible
class Form(TabbedContainer, StrDisplayNameMixin, StrictDefaultChildrenMixin, Content):
    name = models.CharField(verbose_name=_('Name'),
                            max_length=255,
                            default=untitled_form,
                            help_text=_("A name to help identify this form. Only admins see this."))

    # associates instances of the same logical form across versions
    ident = UUIDField()

    editable = True

    default_children = [
        ('fields', FormBody, (), {}),
        ('meta', FormMeta, (), {}),
    ]
    tooltip = _("Use this widget to build a Form that your users can fill out.")

    class FormQuerySet(QuerySet):
        def annotate_submission_count(self):
            return self.extra(select={
                'submission_count':
                'SELECT COUNT(*) FROM form_builder_formsubmission'
                ' WHERE form_ident = form_builder_form.ident'
            })

    objects = FormQuerySet.as_manager()

    class Meta:
        verbose_name = _('form')
        verbose_name_plural = _('forms')

    def __str__(self):
        return self.name

    @classmethod
    def valid_child_of(cls, parent, obj=None):
        for p in list(parent.get_ancestors()) + [parent]:
            if isinstance(p, Form):
                return False
        return super(Form, cls).valid_child_of(parent, obj)

    def build_form_class(self):
        """
        Returns a django.forms.Form class based on my child widgets.
        """
        fields = OrderedDict(
            (child.get_formfield_name(), child.get_formfield())
            for child in self.depth_first_order() if isinstance(child, BaseFormField)
        )

        mixins = []
        for child in self.depth_first_order():
            if hasattr(child, 'get_form_mixins'):
                mixins.extend(child.get_form_mixins())

        return type(str('WidgyForm'), tuple(mixins + [forms.BaseForm]), {'base_fields': fields})

    @property
    def context_var(self):
        return 'form_instance_{node_pk}'.format(node_pk=self.node.pk)

    @property
    def success_key(self):
        """
        Used in the success URL to decide which form's success message
        to show. Collisions are OK because there aren't expected to be
        many forms on one page, and a collision will only result in both
        forms' success messages being shown.
        """
        return friendly_uuid(self.ident)

    def action_url(self, widgy, tried=()):
        # the `tried` argument is just for nice error reporting
        assert widgy, 'get_form_action_url not found in any owners. Tried: %s' % (tried,)

        owner = widgy['owner']
        if hasattr(owner, 'get_form_action_url'):
            return owner.get_form_action_url(self, widgy)
        else:
            return self.action_url(widgy['parent'], tried=tried + (owner,))

    def render(self, context):
        if self.context_var in context:
            # when the form fails validation, the submission view passes
            # the existing instance back to us in the context
            form = context[self.context_var]
        else:
            form = self.build_form_class()()

        request = context.get('request')
        action_url = build_url(
            self.action_url(context['widgy']),
            **{'from': request and (request.GET.get('from') or request.path)}
        )
        ctx = {
            'form': form,
            'action_url': action_url,
            'success': request and request.GET.get('success') == self.success_key,
        }

        with update_context(context, ctx):
            return super(Form, self).render(context)

    def execute(self, request, form):
        # TODO: does this redirect belong here or in the view?  We populate
        # request.GET['form'] in the model, so we should probable handle it in
        # the model too.
        resp = redirect(build_url(
            request.GET['from'],
            success=self.success_key,
        ))
        for child in self.depth_first_order():
            if isinstance(child, FormReponseHandler):
                resp = child.execute(request, form)
            elif isinstance(child, FormSuccessHandler):
                child.execute(request, form)
        return resp

    def make_root(self):
        """
        Turns us into a root node by taking us out of the tree we're in.
        """
        self.node.move(Node.get_last_root_node(),
                       'last-sibling')

    def delete(self, raw=False):
        self.check_frozen()
        # don't delete, just take us out of the tree
        self.make_root()

    def get_fields(self):
        """
        A dictionary of formfield name -> FormField widget
        """
        ret = OrderedDict()
        for child in self.depth_first_order():
            if isinstance(child, FormField):
                ret[child.get_formfield_name()] = child
        return ret

    @property
    def submissions(self):
        """
        All submissions of this logical (not just this version) form.
        """
        return FormSubmission.objects.filter(
            form_ident=self.ident
        ).prefetch_related('values')

    @property
    def submission_count(self):
        # see also objects.annotate_submission_count to prefetch this value
        if hasattr(self, '_submission_count'):
            return self._submission_count

        return self.submissions.count()

    @submission_count.setter
    def submission_count(self, value):
        self._submission_count = value

    @models.permalink
    def submission_url(self):
        return ('admin:%s_%s_change' % (self._meta.app_label, self._meta.model_name),
                (self.pk,),
                {})


class BaseFormField(FormElement):
    formfield_class = None

    class Meta:
        abstract = True

    def get_formfield_name(self):
        return str(self.node.pk)

    def render(self, context):
        form = context['form']
        field = form[self.get_formfield_name()]
        with update_context(context, {'field': field}):
            return super(BaseFormField, self).render(context)

    def get_formfield_kwargs(self):
        return {}

    def get_formfield(self):
        return self.formfield_class(**self.get_formfield_kwargs())

    def get_form_mixins(self):
        """
        A list of mixins to apply to the Django form
        """
        return []


class FormFieldForm(forms.ModelForm):
    help_text = MiniCKEditorField(label=_('help text'), required=False)


@python_2_unicode_compatible
class FormField(StrDisplayNameMixin, BaseFormField):
    widget = None

    label = models.CharField(max_length=255, verbose_name=_('label'))
    required = models.BooleanField(default=True, verbose_name=_('required'))

    help_text = models.TextField(blank=True, verbose_name=_('help text'))
    # associates instances of the same logical field across versions
    ident = UUIDField()

    form = FormFieldForm

    class Meta:
        abstract = True

    def get_formfield_kwargs(self):
        kwargs = super(FormField, self).get_formfield_kwargs()
        kwargs.update({
            'label': self.label,
            'help_text': self.help_text,
            'widget': self.widget,
            'required': self.required,
        })
        return kwargs

    def __str__(self):
        return self.label

    def serialize_value(self, value):
        """
        Used to turn the python object from cleaned_data into a string
        to store in the db. The return value with also be used in the
        CSV download of form data.
        """
        return force_text(value)

    @property
    def widget_attrs(self):
        attrs = {}
        if self.required:
            attrs.update(required='required')
        return attrs


class FormInputForm(FormFieldForm):
    class Meta:
        fields = (
            'type',
            'required',
            'label',
            'help_text',
        )


@widgy.register
class FormInput(FormField):
    FORMFIELD_CLASSES = {
        'text': forms.CharField,
        'number': forms.IntegerField,
        'email': forms.EmailField,
        'tel': PhoneNumberField,
        'checkbox': forms.BooleanField,
        'date': forms.DateField,
    }

    FORM_INPUT_TYPES = (
        ('text', _('Text')),
        ('number', _('Number')),
        ('email', _('Email')),
        ('tel', _('Telephone')),
        ('checkbox', _('Checkbox')),
        ('date', _('Date')),
    )

    formfield_class = forms.CharField
    form = FormInputForm

    type = models.CharField(choices=FORM_INPUT_TYPES, max_length=255, verbose_name=_('type'))

    tooltip = _("A single form input. This widget can accept different types of"
                " input like text, number, or email. See a more complete list"
                " inside the widget.")

    class Meta:
        verbose_name = _('form input')
        verbose_name_plural = _('form inputs')

    @property
    def widget_attrs(self):
        attrs = super(FormInput, self).widget_attrs
        attrs['type'] = self.type

        if self.type == 'date':
            # Use type text because Kalendae doesn't play well with type=date
            attrs['type'] = 'text'
            attrs['class'] = 'date auto-kal'
        return attrs

    @property
    def formfield_class(self):
        return self.FORMFIELD_CLASSES.get(self.type, forms.CharField)

    @property
    def widget(self):
        return self.formfield_class.widget(attrs=self.widget_attrs)


@widgy.register
class Textarea(FormField):
    formfield_class = forms.CharField

    tooltip = _("Add this to your form to allow users to add large amounts of"
                " text.")

    class Meta:
        verbose_name = _('text area')
        verbose_name_plural = _('text areas')

    @property
    def widget(self):
        return forms.Textarea(attrs=self.widget_attrs)


class BaseChoiceField(FormField):
    choices = models.TextField(
        help_text=_("Place each choice on a separate line."))

    class Meta:
        abstract = True

    def get_formfield_kwargs(self):
        kwargs = super(BaseChoiceField, self).get_formfield_kwargs()
        kwargs['choices'] = self.get_choices()
        return kwargs

    def get_choices(self):
        return [(i.strip(), i.strip()) for i in self.choices.splitlines()]

    @property
    def widget(self):
        return self.widget_class(attrs=self.widget_attrs)


@widgy.register
class ChoiceField(BaseChoiceField):
    WIDGET_CLASSES = {
        'select': forms.Select,
        'radios': forms.RadioSelect,
    }

    EMPTY_LABEL = '---------'

    formfield_class = forms.ChoiceField

    type = models.CharField(max_length=25, verbose_name=_('type'), choices=[
        ('select', _('Dropdown')),
        ('radios', _('Radio buttons')),
    ])

    tooltip = _("Use this to allow your users to choose from a list of"
                " options. ChoiceFields can be displayed as radio buttons"
                " or as a dropdown.")

    def get_choices(self):
        choices = super(ChoiceField, self).get_choices()
        if self.type == 'select':
            choices.insert(0, ('', self.EMPTY_LABEL))
        return choices

    @property
    def widget_class(self):
        return self.WIDGET_CLASSES.get(self.type, forms.Select)


@widgy.register
class MultipleChoiceField(BaseChoiceField):
    WIDGET_CLASSES = {
        'checkboxes': forms.CheckboxSelectMultiple,
        'select': forms.SelectMultiple,
    }

    formfield_class = forms.MultipleChoiceField

    type = models.CharField(max_length=25, verbose_name=_('type'), choices=[
        ('checkboxes', _('Checkboxes')),
        ('select', _('Multi-select')),
    ])

    tooltip = _("Use this to allow your users to choose one or more options"
                " from a list of choices. This field can be displayed as"
                " checkboxes or as a multi-select dropdown.")

    @property
    def widget_attrs(self):
        attrs = super(MultipleChoiceField, self).widget_attrs
        if 'required' in attrs and self.type == 'checkboxes':
            # required would go on every single checkbox, which isn't what we
            # want
            del attrs['required']
        return attrs

    def serialize_value(self, value):
        """
        `value` is the list of chosen choices. Join them together with
        commas, escaping literal commas in the choice with a backslash.
        This quoting method was chosen to not cause any ambiguity when
        choices contain commas.
        """
        return ','.join(i.replace('\\', '\\\\').replace(',', '\\,') for i in value)

    @property
    def widget_class(self):
        return self.WIDGET_CLASSES.get(self.type, forms.CheckboxSelectMultiple)


@widgy.register
class Uncaptcha(BaseFormField):
    editable = False
    formfield_class = forms.CharField

    tooltip = _("This widget uses a special script to detect and prevent"
                " spam.")

    def get_form_mixins(self):
        # since validating an uncaptcha widget requires access to the
        # csrfmiddlewaretoken and not just our field value, create a
        # form mixin with a clean_uncaptcha method to do the validation.
        def clean(form):
            value = form.cleaned_data[self.get_formfield_name()]
            if value != form.data.get('csrfmiddlewaretoken'):
                raise forms.ValidationError(_('Incorrect Uncaptcha value'))
        UncaptchaMixin = type(str('UncaptchaMixin'), (object,), {
            'clean_%s' % self.get_formfield_name(): clean
        })
        return [UncaptchaMixin]

    @classmethod
    def valid_child_of(cls, parent, obj=None):
        # only allow 1 uncaptcha per form
        if not isinstance(parent, FormBody):
            return False
        if obj in parent.depth_first_order():
            return True
        if [i for i in parent.depth_first_order() if isinstance(i, cls)]:
            return False
        else:
            return super(Uncaptcha, cls).valid_child_of(parent, obj)

    class Meta:
        verbose_name = _('uncaptcha')
        verbose_name_plural = _('uncaptchas')


@widgy.register
class FileUpload(FormField):
    formfield_class = forms.FileField
    storage = default_storage

    def generate_filename(self, filename):
        return os.path.join(
            'form-uploads',
            self.storage.get_valid_name(os.path.basename(filename))
        )

    def serialize_value(self, value):
        if value:
            filename = self.generate_filename(value.name)
            filename = self.storage.save(filename, value)
            return self.storage.url(filename)
        else:
            return ''


@widgy.register
class ImageUpload(FileUpload):
    formfield_class = forms.ImageField

    class Meta:
        proxy = True


class FormSubmission(models.Model):
    """
    Holds the data from one submission of a Form.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    form_node = models.ForeignKey(Node, on_delete=models.PROTECT, related_name='form_submissions')
    form_ident = models.CharField(max_length=Form._meta.get_field('ident', False).max_length)

    class FormSubmissionQuerySet(QuerySet):
        def get_formfield_labels(self):
            """
            A dictionary of field uuid to field label. We use the label of the
            field that was used by the most recent submission. Note that this
            means only fields that have been submitted will show up here.
            """

            uuids = FormValue.objects.filter(
                submission__in=self,
            ).values('field_ident').distinct().order_by('field_node__path').values_list('field_ident', flat=True)

            ret = OrderedDict([
                ('created_at', ugettext('Created at')),
            ])
            for field_uuid in uuids:
                latest_value = FormValue.objects.filter(
                    field_ident=field_uuid,
                ).order_by('-submission__created_at', '-pk').select_related('field_node')[0]
                ret[field_uuid] = latest_value.get_label()
            return ret

        def as_dictionaries(self):
            return (i.as_dict() for i in self.all())

        def as_ordered_dictionaries(self, order):
            for submission in self.as_dictionaries():
                yield OrderedDict((ident, submission.get(ident, ''))
                                  for ident in order)

        def to_csv(self, output):
            """
            Write out our submissions as csv to output, a file-like object.
            """

            values = self.as_dictionaries()
            headers = self.get_formfield_labels()

            writer = csv.DictWriter(output, list(headers))

            # python2 csv expects bytes, but python3's works in unicode
            if six.PY2:
                def encode(d):
                    return dict(
                        (k, force_bytes(v)) for k, v in d.items()
                    )
            else:
                def encode(d):
                    return d

            writer.writerow(encode(headers))

            for row in values:
                writer.writerow(encode(row))

        def submit(self, form, data):
            submission = self.create(
                form_node=form.node,
                form_ident=form.ident,
            )

            for name, field in form.get_fields().items():
                value = field.serialize_value(data[name])
                submission.values.create(
                    field_node=field.node,
                    field_name=field.label,
                    field_ident=field.ident,
                    value=value,
                )
            return submission

    objects = FormSubmissionQuerySet.as_manager()

    class Meta:
        verbose_name = _('form submission')
        verbose_name_plural = _('form submissions')

    def as_dict(self):
        ret = {'created_at': self.created_at}
        for value in self.values.all():
            ret[value.field_ident] = value.value
        return ret


class FormValue(models.Model):
    """
    Holds a datum from a form submission, EAV style.
    """

    submission = models.ForeignKey(FormSubmission, related_name='values')

    # three references to the form field! field_node is a foreign key to the
    # field at the time of submission, field_ident is the field's uuid to
    # associate submissions of the same logical field across versions, and
    # field_name is our last resort, in case the field has been deleted.
    field_node = models.ForeignKey(Node, on_delete=models.SET_NULL, null=True)
    field_name = models.CharField(max_length=255)
    field_ident = models.CharField(
        max_length=FormField._meta.get_field('ident', False).max_length)

    value = models.TextField()

    def get_label(self):
        if self.field_node:
            return self.field_node.content.label
        else:
            return self.field_name


@receiver(pre_delete_widget, sender=FormInput)
def protect_emailuserhandler_to_ident_field(sender, instance, raw, **kwargs):
    from django.db.models import ProtectedError

    for child in instance.parent_form.depth_first_order():
        if isinstance(child, EmailUserHandler) and child.to_ident == instance.ident:
            raise ProtectedError("This cannot be deleted because it is being referenced by a %s." % (child.display_name,), [child])
