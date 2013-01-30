"""
A collection of model and form field classes.
"""
from django import forms
from django.template.loader import render_to_string
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from django.forms import widgets
from django.contrib.contenttypes.models import ContentType

try:
    from django.utils.html import format_html
except ImportError:
    # Django < 1.5 doesn't have this

    def format_html(format_string, *args, **kwargs):  # NOQA
        """
        Similar to str.format, but passes all arguments through
        conditional_escape, and calls 'mark_safe' on the result. This function
        should be used instead of str.format or % interpolation to build up
        small HTML fragments.
        """
        args_safe = map(conditional_escape, args)
        kwargs_safe = dict([(k, conditional_escape(v)) for (k, v) in kwargs.iteritems()])
        return mark_safe(format_string.format(*args_safe, **kwargs_safe))

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
    stylesheets = None
    template_name = 'widgy/widgy_field.html'

    def render(self, name, value, attrs=None, context={}):
        self.node.maybe_prefetch_tree()
        defaults = {
            'html_name': name,
            'value': value,
            'stylesheets': self.stylesheets,
            'html_id': attrs['id'],
            'node_dict': self.node.to_json(self.site),
        }
        defaults.update(context)
        return render_to_string(self.template_name, defaults)


class ContentTypeRadioInput(widgets.RadioInput):
    def __init__(self, name, value, attrs, choice, index):
        super(ContentTypeRadioInput, self).__init__(name, value, attrs, choice, index)
        self.choice_label = format_html('<span class="label">{0}</span>', self.choice_label)

    def tag(self):
        tag = super(ContentTypeRadioInput, self).tag()
        ct = ContentType.objects.get_for_id(self.choice_value)
        return format_html('<div class="previewImage {0} {1}"></div>{2}', ct.app_label, ct.model, tag)


class ContentTypeRadioRenderer(widgets.RadioFieldRenderer):
    def __iter__(self):
        for i, choice in enumerate(self.choices):
            yield ContentTypeRadioInput(self.name, self.value, self.attrs.copy(), choice, i)

    def __getitem__(self, idx):
        choice = self.choices[idx] # Let the IndexError propogate
        return ContentTypeRadioInput(self.name, self.value, self.attrs.copy(), choice, idx)


class ContentTypeRadioSelect(widgets.RadioSelect):
    renderer = ContentTypeRadioRenderer


class WidgyFormField(forms.ModelChoiceField):
    """
    Django form field that switches its widget based on the context of the
    Node.
    """
    widget = WidgyWidget

    def __init__(self, *args, **kwargs):
        self.site = kwargs.pop('site')
        super(WidgyFormField, self).__init__(*args, **kwargs)

    def conform_to_value(self, value):
        """
        When no root node has been set, we prompt the user to choose one from
        the list of choices.  Otherwise, we set the ``WidgyWidget`` class as
        the widget we use for this field instance.
        """
        choices = list(self.choices)
        if isinstance(value, Node):
            self.node = self.widget.node = value
            try:
                self.widget.stylesheets = self.node.content.editor_stylesheets
            except AttributeError:
                pass
            self.queryset = None
        elif len(choices) == 2:
            self._value = choices[1][0]
            self.widget = DisplayWidget(display_name=choices[1][1])
            self.help_text = 'You must save before you can edit this.'
        else:
            self.widget = ContentTypeRadioSelect(
                # remove the empty choice
                choices=[c for c in choices if c[0]]
            )

        self.widget.site = self.site

    def clean(self, value):
        value = getattr(self, '_value', value)

        try:
            value = super(WidgyFormField, self).clean(value)
        except:
            if self.node:
                value = self.node
            else:
                raise

        return value


class VersionedWidgyWidget(WidgyWidget):
    template_name = 'widgy/versioned_widgy_field.html'

    def render(self, name, value, attrs=None):
        context = {
            'commit_url': self.site.reverse(self.site.commit_view, kwargs={'pk': value}),
        }
        return super(VersionedWidgyWidget, self).render(name, value, attrs, context)


class VersionedWidgyFormField(WidgyFormField):
    widget = VersionedWidgyWidget

    def conform_to_value(self, value):
        self.version_tracker = value
        return super(VersionedWidgyFormField, self).conform_to_value(value and value.working_copy)

    def clean(self, value):
        return self.version_tracker or super(VersionedWidgyFormField, self).clean(value)


class WidgyFormMixin(object):
    """
    Form mixin that enables the widget switching by calling
    :meth:`~WidgyFormField.conform_to_value` on the field instance.
    """
    def __init__(self, *args, **kwargs):
        super(WidgyFormMixin, self).__init__(*args, **kwargs)

        for name, field in self.fields.iteritems():
            if isinstance(field, WidgyFormField):
                value = getattr(self.instance, name)
                field.conform_to_value(value)
