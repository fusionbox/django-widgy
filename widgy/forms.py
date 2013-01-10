"""
A collection of model and form field classes.
"""
from django import forms
from django.template.loader import render_to_string
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

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

    def render(self, name, value, attrs=None):
        self.node.maybe_prefetch_tree()
        return render_to_string('widgy/widgy_field.html', {
            'html_name': name,
            'value': value,
            'stylesheets': self.stylesheets,
            'html_id': attrs['id'],
            'node_dict': self.node.to_json(self.site),
        })


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
            self.widget = forms.Select(
                choices=choices,
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
