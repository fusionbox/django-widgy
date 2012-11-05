"""
A collection of model and form field classes.
"""
from operator import or_

from django.db import models
from django.db.models import Q
from django.db.models.fields.related import ReverseSingleRelatedObjectDescriptor
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.utils.safestring import mark_safe

from fusionbox.core.templatetags.fusionbox_tags import json
from south.modelsinspector import add_introspection_rules
from widgy.models import Node

add_introspection_rules([], ["^widgy\.forms\.WidgyField"])

WIDGY_FIELD_TEMPLATE = u"""
<input type="hidden" name="{name}" value="{value}">
<script data-main="/static/widgy/js/main" src="/static/widgy/js/require/require.js"></script>
<div id="{html_id}" class="widgy"></div>
<script>
  require([ 'widgy' ], function(Widgy) {{
    window.widgy = new Widgy('#{html_id}', {json});
  }});
</script>
"""


class WidgyWidget(forms.HiddenInput):
    """
    Django form widget that is used to load the backbone.js application code
    for a Widgy field.
    """
    def render(self, name, value, attrs=None):
        node_json = json(self.node.to_json())
        return mark_safe(WIDGY_FIELD_TEMPLATE.format(
            name=name,
            value=value,
            html_id=attrs['id'],
            json=node_json,
        ))


class WidgyFormField(forms.ModelChoiceField):
    """
    Django form field that switches its widget based on the context of the
    Node.
    """
    widget = WidgyWidget #: default widget

    def conform_to_value(self, value):
        """
        When no root node has been set, we prompt the user to choose one from
        the list of choices.  Otherwise, we set the ``WidgyWidget`` class as
        the widget we use for this field instance.
        """
        if isinstance(value, Node):
            self.node = self.widget.node = value
            self.queryset = None
        else:
            self.widget = forms.Select(
                choices=self.choices,
            )

    def clean(self, value):
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
