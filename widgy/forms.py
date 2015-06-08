from __future__ import unicode_literals
import time

from django import forms
from django.template.loader import render_to_string
from django.forms import widgets
from django.contrib.contenttypes.models import ContentType
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.utils.html import format_html
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.template.defaultfilters import capfirst

from widgy.models import Node


class DisplayWidget(forms.Widget):
    def __init__(self, display_name, *args, **kwargs):
        super(DisplayWidget, self).__init__(*args, **kwargs)
        self.display_name = display_name

    def render(self, *args, **kwargs):
        return format_html(u'<span>{name}</span>', name=self.display_name)


class WidgyWidget(forms.HiddenInput):
    """
    Django form widget that is used to load the backbone.js application code
    for a Widgy field.
    """
    template_name = 'widgy/widgy_field.html'
    is_hidden = False

    def render(self, name, value, attrs=None, context={}):
        # If this fails, perhaps they aren't using the WidgyFormMixin.  If you
        # can't use the WidgyFormMixin (report it) and make sure that you call
        # conform_to_value on the WidgyFormField.
        assert hasattr(self, 'node'), "You must set the node on a WidgyWidget prior to rendering it."

        self.node.maybe_prefetch_tree()
        defaults = {
            'html_name': name,
            'value': value,
            'html_id': attrs['id'],
            'node_dict': self.node.to_json(self.site),
            'node': self.node,
            'api_url': reverse(self.site.node_view),
            'site': self.site,
            'owner': self.owner,
        }

        if settings.DEBUG:
            defaults['cachebust'] = time.time()

        defaults.update(context)
        return render_to_string(self.template_name, defaults)


class ContentTypeRadioInput(widgets.RadioChoiceInput):
    def __init__(self, name, value, attrs, choice, index):
        super(ContentTypeRadioInput, self).__init__(name, value, attrs, choice, index)
        self.choice_label = format_html('<span class="label">{0}</span>', self.choice_label)

    def tag(self, attrs=None):
        if attrs is None:
            # BBB Django < 1.8 tag doesn't take any arguments
            tag = super(ContentTypeRadioInput, self).tag()
        else:
            tag = super(ContentTypeRadioInput, self).tag(attrs)
        ct = ContentType.objects.get_for_id(self.choice_value)
        return format_html('<div class="previewImage {0} {1}"></div>{2}', ct.app_label, ct.model, tag)


class ContentTypeRadioRenderer(widgets.RadioFieldRenderer):
    choice_input_class = ContentTypeRadioInput

    # BBB django < 1.7 doesn't use choice_input_class
    def __iter__(self):
        for i, choice in enumerate(self.choices):
            yield self.choice_input_class(self.name, self.value, self.attrs.copy(), choice, i)

    def __getitem__(self, idx):
        choice = self.choices[idx]  # Let the IndexError propogate
        return self.choice_input_class(self.name, self.value, self.attrs.copy(), choice, idx)


class ContentTypeRadioSelect(widgets.RadioSelect):
    renderer = ContentTypeRadioRenderer

    def render(self, *args, **kwargs):
        return (mark_safe('<div class="layoutSelect">') +
                super(ContentTypeRadioSelect, self).render(*args, **kwargs) +
                mark_safe('</div>') +
                render_to_string('widgy/layout_css.html'))


class WidgyFormField(forms.ModelChoiceField):
    """
    Django form field that switches its widget based on the context of the
    Node.
    """
    widget = WidgyWidget

    def __init__(self, *args, **kwargs):
        self.site = kwargs.pop('site')
        super(WidgyFormField, self).__init__(*args, **kwargs)

    def conform_to_value(self, owner, value):
        """
        When no root node has been set, we prompt the user to choose one from
        the list of choices.  Otherwise, we set the ``WidgyWidget`` class as
        the widget we use for this field instance.
        """
        self.owner = owner
        if isinstance(value, Node):
            self.node = value
            try:
                # Sometimes the WidgyWidget is wrapped in a
                # RelatedFieldWidgetWrapper
                self.widget.widget.node = value
            except AttributeError:
                self.widget.node = value
            self.queryset = None
        else:
            # remove the empty choice
            choices = [c for c in self.choices if c[0]]
            if len(choices) == 1:
                self._value = choices[0][0]
                self.widget = DisplayWidget(display_name=choices[0][1])
                self.help_text = _('You must save before you can edit this.')
            else:
                self.widget = ContentTypeRadioSelect(
                    choices=choices,
                )

        try:
            self.widget.widget.site = self.site
            self.widget.widget.owner = owner
        except AttributeError:
            self.widget.site = self.site
            self.widget.owner = owner

    def clean(self, value):
        value = getattr(self, '_value', value)

        try:
            value = super(WidgyFormField, self).clean(value)
        except:
            if getattr(self, 'node', None):
                value = self.node
            else:
                raise

        return value

    def label_from_instance(self, obj):
        ModelClass = obj.model_class()
        if ModelClass:
            return capfirst(ModelClass._meta.verbose_name)
        else:
            return super(WidgyFormField, self).label_from_instance(obj)


class VersionedWidgyWidget(WidgyWidget):
    template_name = ['widgy/versioned_widgy_field.html',
                     'widgy/versioned_widgy_field_base.html']

    def render(self, name, value, attrs=None):
        context = {
            'commit_url': self.site.reverse(self.site.commit_view, kwargs={'pk': value}),
            'reset_url': self.site.reverse(self.site.reset_view, kwargs={'pk': value}),
            'history_url': self.site.reverse(self.site.history_view, kwargs={'pk': value}),
        }

        return super(VersionedWidgyWidget, self).render(name, value, attrs, context)


class VersionedWidgyFormField(WidgyFormField):
    widget = VersionedWidgyWidget

    def conform_to_value(self, owner, value):
        self.version_tracker = value
        super(VersionedWidgyFormField, self).conform_to_value(owner, value and value.working_copy)

    def clean(self, value):
        return self.version_tracker or super(VersionedWidgyFormField, self).clean(value)


class WidgyFormMixin(object):
    """
    Form mixin that enables the widget switching by calling
    :meth:`~WidgyFormField.conform_to_value` on the field instance.
    """
    def __init__(self, *args, **kwargs):
        super(WidgyFormMixin, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            if isinstance(field, WidgyFormField):
                try:
                    value = getattr(self.instance, name)
                except ObjectDoesNotExist:
                    value = None
                field.conform_to_value(self.instance, value)


class WidgyForm(WidgyFormMixin, forms.ModelForm):
    pass
