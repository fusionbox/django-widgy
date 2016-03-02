import copy
from operator import or_
import itertools
from six.moves import reduce

from django.db import models
from django.db.models.fields import Field
from django.contrib.contenttypes.models import ContentType
from django.template.defaultfilters import capfirst
from django import forms
from django.utils.encoding import force_text

try:
    from django.apps import apps
    get_models = apps.get_models
    del apps
except ImportError:
    # Django < 1.8
    from django.db.models import get_models

from widgy.generic import WidgyGenericForeignKey
from widgy import BaseRegistry
from widgy.utils import model_has_field


class LinkRegistry(BaseRegistry):
    def get_links(self, obj):
        if not isinstance(obj, tuple(self)):
            raise ValueError("The object class is not registered linkable")
        all_qs = (linker._default_manager.filter(points_to_links(linker, obj))
                  for linker in self.get_all_linker_classes())

        return itertools.chain.from_iterable(all_qs)

    @classmethod
    def get_all_linker_classes(cls):
        return filter(cls.has_link, get_models())

    @classmethod
    def has_link(cls, model):
        return any(isinstance(field, LinkField)
                   for field in model._meta.virtual_fields)



link_registry = LinkRegistry()
register = link_registry.register
unregister = link_registry.unregister


def points_to_links(linker, linkable):
    """
    Returns a Q object that filters for the linkable instance across all
    LinkFields on the linker model.
    """
    content_type = ContentType.objects.get_for_model(linkable)
    return reduce(or_, (models.Q(**{field.ct_field: content_type,
                                    field.fk_field: linkable.pk})
                        for field in linker._meta.virtual_fields
                        if isinstance(field, LinkField)))


class LinkField(WidgyGenericForeignKey):
    """
    TODO: Explore the consequences of using add_field in contribute_to_class to
    make this a real field instead of a virtual_field.
    """
    def __init__(self, ct_field=None, fk_field=None, *args, **kwargs):
        self.null = kwargs.pop('null', False)
        self._link_registry = kwargs.pop('link_registry', link_registry)
        super(LinkField, self).__init__(ct_field, fk_field, *args, **kwargs)

    def get_choices(self):
        return itertools.chain.from_iterable(choices for _, choices in self.get_choices_by_class())

    def get_choices_by_class(self):
        def key(cls):
            return cls._meta.verbose_name_plural.lower()
        return ((Model, Model._default_manager.all())
                for Model in sorted(self._link_registry, key=key))

    def contribute_to_class(self, cls, name):
        if self.ct_field is None:
            self.ct_field = '%s_content_type' % name

        if self.fk_field is None:
            self.fk_field = '%s_object_id' % name

        # do not do anything that loads the app cache here, like
        # _meta.get_all_field_names, or you'll cause a circular import.
        if not model_has_field(cls, self.ct_field):
            ct_field = models.ForeignKey(ContentType, related_name='+',
                                         null=self.null, editable=False)
            cls.add_to_class(self.ct_field, ct_field)

        if not model_has_field(cls, self.fk_field):
            fk_field = models.PositiveIntegerField(null=self.null,
                                                   editable=False)
            cls.add_to_class(self.fk_field, fk_field)

        super(LinkField, self).contribute_to_class(cls, name)

    def __deepcopy__(self, memodict):
        # Copied from Field.__deepcopy__ to avoid copying _link_registry
        obj = copy.copy(self)
        memodict[id(self)] = obj
        return obj


def get_composite_key(linkable):
    content_type = ContentType.objects.get_for_model(linkable)
    return u'%s-%s' % (content_type.pk, linkable.pk)


def convert_linkable_to_choice(linkable):
    key = get_composite_key(linkable)

    try:
        value = u'%s (%s)' % (force_text(linkable), linkable.get_absolute_url())
    except AttributeError:
        value = force_text(linkable)

    return (key, value)


class LinkFormField(forms.ChoiceField):
    def __init__(self, choices=(), empty_label="---------", *args, **kwargs):
        self.empty_label = empty_label
        super(LinkFormField, self).__init__(choices, *args, **kwargs)

    def clean(self, value):
        content_type_pk, _, object_pk = value.partition('-')
        if object_pk:
            content_type = ContentType.objects.get_for_id(content_type_pk)
            return content_type.get_object_for_this_type(pk=object_pk)
        else:
            return None

    def populate_choices(self, choice_map):
        keyfn = lambda x: x[1].lower()

        choices = [(capfirst(Model._meta.verbose_name_plural),
                    sorted(map(convert_linkable_to_choice, choices), key=keyfn))
                   for Model, choices in choice_map
                   if len(choices)]

        if not self.required and self.empty_label is not None:
            choices.insert(0, ('', self.empty_label))

        self.choices = choices


def get_link_field_from_model(model, name):
    for field in model._meta.virtual_fields:
        if isinstance(field, LinkField) and field.name == name:
            return field


class LinkFormMixin(object):
    def __init__(self, *args, **kwargs):
        super(LinkFormMixin, self).__init__(*args, **kwargs)
        for name, field in self.get_link_form_fields():
            value = getattr(self.instance, name, None)
            model_field = get_link_field_from_model(self.instance, name)
            field.initial = get_composite_key(value) if value else None
            field.populate_choices(model_field.get_choices_by_class())

    def get_link_form_fields(self):
        return ((name, field)
                for name, field in self.fields.items()
                if isinstance(field, LinkFormField))

    def save(self, *args, **kwargs):
        if not self.errors:
            cleaned_data = self.cleaned_data

            for name, field in self.get_link_form_fields():
                setattr(self.instance, name, cleaned_data[name])

        return super(LinkFormMixin, self).save(*args, **kwargs)
