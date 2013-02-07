from django.db import models
from django import forms
from django.utils.datastructures import SortedDict
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.db.models.query import QuerySet

from fusionbox import behaviors
from fusionbox.db.models import QuerySetManager
from django_extensions.db.fields import UUIDField

from widgy.models import Content, Node
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


class FormSuccessHandler(FormElement):
    draggable = False

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
class SaveDataHandler(FormSuccessHandler):
    editable = False

    def execute(self, request, form):
        FormSubmission.objects.submit(
            form=self.parent_form,
            data=form.cleaned_data
        )


@widgy.register
class SubmitButton(DefaultChildrenMixin, FormElement):
    text = models.CharField(max_length=255, default='submit')

    default_children = [
        (SaveDataHandler, (), {}),
    ]

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


def untitled_form():
    n = Form.objects.filter(name__startswith='Untitled form ').exclude(
        _nodes__is_frozen=True
    ).count() + 1
    return 'Untitled form %d' % n


@widgy.register
class Form(DefaultChildrenMixin, Content):
    name = models.CharField(max_length=255,
                            default=untitled_form,
                            help_text="A name to help identify this form. Only admins see this.")

    # associates instances of the same logical form across versions
    ident = UUIDField()

    accepting_children = True
    shelf = True
    editable = True

    default_children = [
        (SubmitButton, (), {}),
    ]

    objects = QuerySetManager()

    class QuerySet(QuerySet):
        def annotate_submission_count(self):
            return self.extra(select={
                'submission_count':
                'SELECT COUNT(*) FROM form_builder_formsubmission'
                ' WHERE form_ident = form_builder_form.ident'
            })

    def __unicode__(self):
        return self.name

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
                            for child in self.depth_first_order() if isinstance(child, BaseFormField))

        mixins = []
        for child in self.depth_first_order():
            if hasattr(child, 'get_form_mixins'):
                mixins.extend(child.get_form_mixins())

        return type('WidgyForm', tuple(mixins + [forms.BaseForm]), {'base_fields': fields})

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


class FormField(BaseFormField):
    widget = None

    label = models.CharField(max_length=255)
    required = models.BooleanField(default=True)

    help_text = models.TextField(blank=True)
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


FORM_INPUT_TYPES = (
    ('text', 'Text'),
    ('number', 'Number'),
)

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
    formfield_class = forms.CharField
    form = FormInputForm

    type = models.CharField(choices=FORM_INPUT_TYPES, max_length=255)


@widgy.register
class Textarea(FormField):
    formfield_class = forms.CharField
    widget = forms.Textarea


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
                raise forms.ValidationError('Incorrect Uncaptcha value')
        UncaptchaMixin = type('UncaptchaMixin', (object,), {
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
                submission.values.create(
                    field_node=field.node,
                    field_name=field.label,
                    field_ident=field.ident,
                    value=data[name]
                )
            return submission

    def as_dict(self):
        ret = {}
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
        max_length=FormField._meta.get_field_by_name('ident')[0].max_length)

    value = models.TextField()

    def get_label(self):
        if self.field_node:
            return self.field_node.content.label
        else:
            return self.field_name
