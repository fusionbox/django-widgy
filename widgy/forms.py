"""
A collection of model and form field classes.
"""
from operator import or_

from django.db import models
from django.db.models import Q
from django.db.models.fields.related import ReverseSingleRelatedObjectDescriptor
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.template import Context
from django.template.loader import get_template
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

try:
    from django.utils.html import format_html
except ImportError:
    # Django < 1.5 doesn't have this

    def format_html(format_string, *args, **kwargs): # NOQA
        """
        Similar to str.format, but passes all arguments through
        conditional_escape, and calls 'mark_safe' on the result. This function
        should be used instead of str.format or % interpolation to build up
        small HTML fragments.
        """
        args_safe = map(conditional_escape, args)
        kwargs_safe = dict([(k, conditional_escape(v)) for (k, v) in kwargs.iteritems()])
        return mark_safe(format_string.format(*args_safe, **kwargs_safe))

from south.modelsinspector import add_introspection_rules
from widgy.models import Node

add_introspection_rules([], ["^widgy\.forms\.WidgyField"])


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
        t = get_template('widgy/widgy_field.html')
        self.node.maybe_prefetch_tree()
        return t.render(Context({
            'name': name,
            'value': value,
            'stylesheets': self.stylesheets,
            'html_id': attrs['id'],
            'node': self.node,
        }))


class WidgyFormField(forms.ModelChoiceField):
    """
    Django form field that switches its widget based on the context of the
    Node.
    """
    widget = WidgyWidget

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


class WidgyFieldObjectDescriptor(ReverseSingleRelatedObjectDescriptor):
    """
    .. note::
        we need to transport the ContentType of the Node all the way to
        ``pre_save``, without saving an instance of the node, because we don't
        know if the rest of the model is valid yet.
    """
    def __set__(self, instance, value):
        """
        """
        if isinstance(value, ContentType):
            value, value._ct = self.field.rel.to(), value

        super(WidgyFieldObjectDescriptor, self).__set__(instance, value)


class WidgyField(models.ForeignKey):
    """
    Model field that inherits from ``models.ForeignKey``.  Contains validation
    and context switching that is needed for Widgy fields.
    """
    def __init__(self, to=None, root_choices=None, **kwargs):
        if to is None:
            to = 'widgy.Node'

        self.root_choices = root_choices

        defaults = {
            'blank': True,
            'null': True,
            'on_delete': models.SET_NULL
        }
        defaults.update(kwargs)

        super(WidgyField, self).__init__(to, **defaults)

    def contribute_to_class(self, cls, name):
        """

        .. note:: we need to use WidgyFieldObjectDescriptor instead of
            ``ReverseSingleRelatedObjectDescriptor`` because of the modifications
            to __set__.
        """
        super(WidgyField, self).contribute_to_class(cls, name)
        setattr(cls, self.name, WidgyFieldObjectDescriptor(self))

    def pre_save(self, model_instance, add):
        """
        Relies on WidgyFieldObjectDescriptor to set the content type on an
        unsaved throwaway Node so that we know how to properly instantiate a
        real node later on.
        """
        value = getattr(model_instance, self.name)

        if hasattr(value, '_ct'):
            ct = value._ct

            node = ct.model_class().add_root().node
            setattr(model_instance, self.name, node)
            setattr(model_instance, self.attname, node.pk)

            return node.pk

        return super(WidgyField, self).pre_save(model_instance, add)

    def formfield(self, **kwargs):
        defaults = {
            'form_class': WidgyFormField,
            'queryset': self.get_layout_contenttypes(self.root_choices),
        }
        defaults.update(kwargs)
        return super(WidgyField, self).formfield(**defaults)

    def get_layout_contenttypes(self, layouts):
        qs = []

        for layout in layouts:
            try:
                app_label, model_name = layout.split(".")
            except ValueError:
                app_label = self.model._meta.app_label
                model_name = layout
            except AttributeError:
                app_label = layout._meta.app_label
                model_name = layout._meta.object_name

            cls = models.get_model(app_label, model_name, seed_cache=False, only_installed=False)

            qs.append(Q(app_label=app_label, model=cls._meta.module_name))

        return ContentType.objects.filter(reduce(or_, qs))
