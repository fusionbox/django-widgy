from operator import or_

from django.db import models
from django.db.models import Q
from django.db.models.fields.related import ReverseSingleRelatedObjectDescriptor
from django.db.models.loading import get_app
from django.contrib.contenttypes.models import ContentType
from django.utils.functional import SimpleLazyObject

from widgy.site import WidgySite
from widgy.forms import WidgyFormField
from widgy.utils import fancy_import

from south.modelsinspector import add_introspection_rules

add_introspection_rules([], ["^widgy\.db.fields\.WidgyField"])


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
    def __init__(self, site=None, to=None, root_choices=None, **kwargs):
        if to is None:
            to = 'widgy.Node'

        self.root_choices = root_choices

        defaults = {
            'blank': True,
            'null': True,
            'on_delete': models.SET_NULL
        }
        defaults.update(kwargs)

        if isinstance(site, WidgySite):
            self.site = site
        else:
            # prevent a circular import by lazily importing the site
            self.site = SimpleLazyObject(lambda: fancy_import(site))

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

            node = ct.model_class().add_root(self.site).node
            setattr(model_instance, self.name, node)
            setattr(model_instance, self.attname, node.pk)

            return node.pk

        return super(WidgyField, self).pre_save(model_instance, add)

    def formfield(self, **kwargs):
        defaults = {
            'form_class': WidgyFormField,
            'queryset': self.get_layout_contenttypes(self.root_choices),
            'site': self.site,
        }
        defaults.update(kwargs)
        return super(WidgyField, self).formfield(**defaults)

    def get_layout_contenttypes(self, layouts):
        def normalize(layout):
            try:
                app_label, model_name = layout.split(".")
            except ValueError:
                app_label = self.model._meta.app_label
                model_name = layout
            except AttributeError:
                app_label = layout._meta.app_label
                model_name = layout._meta.object_name

            # we cannot use models.get_model because this class could be
            # abstract.
            return getattr(get_app(app_label), model_name)

        layouts = tuple(map(normalize, layouts))
        classes = (cls for cls in self.site.get_all_content_classes() if issubclass(cls, layouts))

        qs = reduce(or_, (Q(app_label=cls._meta.app_label, model=cls._meta.module_name)
                          for cls in classes))

        # we need to return a queryset, not a list.
        return ContentType.objects.filter(qs)
