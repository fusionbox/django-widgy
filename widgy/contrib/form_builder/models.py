from __future__ import unicode_literals

from django.db import models
from django import forms
from django.utils.datastructures import SortedDict
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.db.models.query import QuerySet
from django.utils.translation import ugettext_lazy as _, ugettext
from django.shortcuts import redirect

from fusionbox import behaviors
from fusionbox.db.models import QuerySetManager
from django_extensions.db.fields import UUIDField
from fusionbox.forms.fields import PhoneNumberField

from widgy.models import Content, Node
from widgy.models.mixins import StrictDefaultChildrenMixin, DefaultChildrenMixin, TabbedContainer, DisplayNameMixin
from widgy.utils import update_context, build_url
from widgy.contrib.page_builder.db.fields import MarkdownField
from widgy.contrib.page_builder.models import Bucket, Html
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
    draggable = False

    class Meta:
        abstract = True

    @classmethod
    def valid_child_of(cls, parent, obj=None):
        return isinstance(parent, SuccessHandlers)


class FormReponseHandler(FormSuccessHandler):
    class Meta:
        abstract = True


@widgy.register
class EmailSuccessHandler(FormSuccessHandler):
    to = models.EmailField(verbose_name=_('to'))
    subject = models.CharField(max_length=255, verbose_name=_('subject'))
    content = MarkdownField(blank=True, verbose_name=_('content'))

    component_name = 'markdown'

    def execute(self, request, form):
        send_markdown_mail(self.subject, self.content, settings.SERVER_EMAIL, [self.to])

    class Meta:
        verbose_name = _('admin success email')
        verbose_name_plural = _('admin success emails')


@widgy.register
class SaveDataHandler(FormSuccessHandler):
    editable = False

    def execute(self, request, form):
        FormSubmission.objects.submit(
            form=self.parent_form,
            data=form.cleaned_data
        )

    class Meta:
        verbose_name = _('save data handler')
        verbose_name_plural = _('save data handlers')


class EmailUserHandlerForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EmailUserHandlerForm, self).__init__(*args, **kwargs)
        self.fields['to'].queryset = Node.objects.filter(
            id__in=[i.node.id for i in self.instance.get_email_fields()]
        )


def send_markdown_mail(subject, content, from_email, to):
    from widgy.templatetags.widgy_tags import mdown
    msg = EmailMultiAlternatives(subject, content, from_email, to)
    msg.attach_alternative(mdown(content), 'text/html')
    msg.send()


@widgy.register
class EmailUserHandler(FormSuccessHandler):
    editable = True
    component_name = 'markdown'
    form = EmailUserHandlerForm

    # an input in our form
    to = models.ForeignKey(Node, related_name='+', null=True, verbose_name=_('to'))
    subject = models.CharField(max_length=255, verbose_name=_('subject'))
    content = MarkdownField(blank=True, verbose_name=_('content'))

    def execute(self, request, form):
        to = self.to.content
        to_email = form.cleaned_data[to.get_formfield_name()]
        send_markdown_mail(self.subject, self.content, settings.SERVER_EMAIL, [to_email])

    def get_email_fields(self):
        return [i for i in self.parent_form.depth_first_order()
                if isinstance(i, FormInput) and i.type == 'email']

    def post_create(self, site):
        email_fields = self.get_email_fields()
        if email_fields:
            self.to = email_fields[0].node
        self.save()

    class Meta:
        verbose_name = _('user success email')
        verbose_name_plural = _('user success emails')


@widgy.register
class SubmitButton(FormElement):
    text = models.CharField(max_length=255, default=lambda: ugettext('submit'), verbose_name=_('text'))

    @property
    def deletable(self):
        return len([i for i in self.parent_form.depth_first_order() if isinstance(i, SubmitButton)]) > 1

    class Meta:
        verbose_name = _('submit button')
        verbose_name_plural = _('submit buttons')


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


@widgy.register
class Form(TabbedContainer, DisplayNameMixin(lambda x: x.name), StrictDefaultChildrenMixin, Content):
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

    objects = QuerySetManager()

    class Meta:
        verbose_name = _('form')
        verbose_name_plural = _('forms')

    class QuerySet(QuerySet):
        def annotate_submission_count(self):
            return self.extra(select={
                'submission_count':
                'SELECT COUNT(*) FROM form_builder_formsubmission'
                ' WHERE form_ident = form_builder_form.ident'
            })

    def __unicode__(self):
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
        fields = SortedDict((child.get_formfield_name(), child.get_formfield())
                            for child in self.depth_first_order() if isinstance(child, BaseFormField))

        mixins = []
        for child in self.depth_first_order():
            if hasattr(child, 'get_form_mixins'):
                mixins.extend(child.get_form_mixins())

        return type(str('WidgyForm'), tuple(mixins + [forms.BaseForm]), {'base_fields': fields})

    @property
    def context_var(self):
        return 'form_instance_{node_pk}'.format(node_pk=self.node.pk)

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
            'success': request and request.GET.get('success') == str(self.node.pk),
        }

        with update_context(context, ctx):
            return super(Form, self).render(context)

    def execute(self, request, form):
        # TODO: does this redirect belong here or in the view?  We populate
        # request.GET['form'] in the model, so we should probable handle it in
        # the model too.
        resp = redirect(build_url(
            request.GET['from'],
            success=self.node.pk,
        ))
        # TODO: only call the handlers for the submit button that was pressed.
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

    def delete(self):
        self.check_frozen()
        # don't delete, just take us out of the tree
        self.make_root()

    def get_fields(self):
        """
        A dictionary of formfield name -> FormField widget
        """
        ret = {}
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
        return ('admin:%s_%s_change' % (self._meta.app_label, self._meta.module_name),
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


class FormField(DisplayNameMixin(lambda x: x.label), BaseFormField):
    widget = None

    label = models.CharField(max_length=255, verbose_name=_('label'))
    required = models.BooleanField(default=True, verbose_name=_('required'))

    help_text = models.TextField(blank=True, verbose_name=_('help text'))
    # associates instances of the same logical field across versions
    ident = UUIDField()

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

    def __unicode__(self):
        return self.label

    def serialize_value(self, value):
        """
        Used to turn the python object from cleaned_data into a string
        to store in the db. The return value with also be used in the
        CSV download of form data.
        """
        return unicode(value)


class FormInputForm(forms.ModelForm):
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
    }

    FORM_INPUT_TYPES = (
        ('text', _('Text')),
        ('number', _('Number')),
        ('email', _('Email')),
        ('tel', _('Telephone')),
    )

    formfield_class = forms.CharField
    form = FormInputForm

    type = models.CharField(choices=FORM_INPUT_TYPES, max_length=255, verbose_name=_('type'))

    @property
    def formfield_class(self):
        return self.FORMFIELD_CLASSES[self.type]

    @property
    def widget(self):
        attrs = {
            'type': self.type,
        }
        if self.required:
            attrs['required'] = 'required'

        return forms.TextInput(attrs=attrs)

    class Meta:
        verbose_name = _('form input')
        verbose_name_plural = _('form inputs')


@widgy.register
class Textarea(FormField):
    formfield_class = forms.CharField

    @property
    def widget(self):
        attrs = {}
        if self.required:
            attrs['required'] = 'required'
        return forms.Textarea(attrs=attrs)

    class Meta:
        verbose_name = _('text area')
        verbose_name_plural = _('text areas')


class BaseChoiceField(FormField):
    choices = models.TextField()

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
        attrs = self.widget_attrs
        return self.widget_class(attrs=attrs)

    @property
    def widget_attrs(self):
        return {
            'required': self.required,
        }

    @property
    def widget_class(self):
        return self.WIDGET_CLASSES[self.type]


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

    def get_choices(self):
        choices = super(ChoiceField, self).get_choices()
        if self.type == 'select':
            choices.insert(0, ('', self.EMPTY_LABEL))
        return choices


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


@widgy.register
class Uncaptcha(BaseFormField):
    editable = False
    formfield_class = forms.CharField

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
        if not isinstance(parent, Form):
            return False
        if obj in parent.get_children():
            return True
        if [i for i in parent.get_children() if isinstance(i, cls)]:
            return False
        else:
            return super(Uncaptcha, cls).valid_child_of(parent, obj)

    class Meta:
        verbose_name = _('uncaptcha')
        verbose_name_plural = _('uncaptchas')


class FormSubmission(behaviors.Timestampable, models.Model):
    """
    Holds the data from one submission of a Form.
    """

    form_node = models.ForeignKey(Node, on_delete=models.PROTECT, related_name='form_submissions')
    form_ident = models.CharField(max_length=Form._meta.get_field_by_name('ident')[0].max_length)

    objects = QuerySetManager()

    class QuerySet(QuerySet):
        def field_names(self):
            """
            A dictionary of field uuid to field label. We use the label of the
            field that was used by the most recent submission. Note that this
            means only fields that have been submitted will show up here.
            """

            uuids = FormValue.objects.filter(
                submission__in=self,
            ).values('field_ident').distinct().values_list('field_ident', flat=True)

            ret = {}
            for field_uuid in uuids:
                latest_value = FormValue.objects.filter(
                    field_ident=field_uuid,
                ).order_by('-submission__created_at', '-pk').select_related('field_node')[0]
                ret[field_uuid] = latest_value.get_label()
            return ret

        def as_dictionaries(self):
            return (i.as_dict() for i in self.all())

        def submit(self, form, data):
            submission = self.create(
                form_node=form.node,
                form_ident=form.ident,
            )

            for name, field in form.get_fields().iteritems():
                value = field.serialize_value(data[name])
                submission.values.create(
                    field_node=field.node,
                    field_name=field.label,
                    field_ident=field.ident,
                    value=value,
                )
            return submission

    def as_dict(self):
        ret = {}
        for value in self.values.all():
            ret[value.field_ident] = value.value
        return ret

    class Meta:
        verbose_name = _('form submission')
        verbose_name_plural = _('form submissions')


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
        max_length=FormField._meta.get_field_by_name('ident')[0].max_length)

    value = models.TextField()

    def get_label(self):
        if self.field_node:
            return self.field_node.content.label
        else:
            return self.field_name
