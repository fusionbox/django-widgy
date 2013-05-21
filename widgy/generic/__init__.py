import django
from django.contrib.contenttypes import generic
from django.db import DEFAULT_DB_ALIAS, connection
from widgy.generic.models import ContentType

from south.modelsinspector import add_ignored_fields

add_ignored_fields(["^widgy\.generic\.ProxyGenericRelation",
                    "^widgy\.generic\.ProxyGenericForeignKey",
                    "^widgy\.generic\.WidgyGenericForeignKey"])

if django.VERSION >= (1, 6):
    class ProxyGenericForeignKey(generic.GenericForeignKey):
        def __init__(self, *args, **kwargs):
            kwargs['for_concrete_model'] = False
            super(ProxyGenericForeignKey, self).__init__(*args, **kwargs)

    class ProxyGenericRelation(generic.GenericRelation):
        def __init__(self, *args, **kwargs):
            kwargs['for_concrete_model'] = False
            super(ProxyGenericRelation, self).__init__(*args, **kwargs)
else:
    class ProxyGenericForeignKey(generic.GenericForeignKey):
        """
        A GenericForeignKey that can point to a proxy model.
        """

        def get_content_type(self, obj=None, id=None, using=None):
            if obj:
                return ContentType.objects.db_manager(obj._state.db).get_for_model(
                    obj,
                    for_concrete_model=False)
            else:
                return super(ProxyGenericForeignKey, self).get_content_type(obj, id, using)


    class ProxyGenericRelation(generic.GenericRelation):
        def get_content_type(self):
            """
            Returns the content type associated with this field's model.
            """
            return ContentType.objects.get_for_model(self.model, for_concrete_model=False)

        def extra_filters(self, pieces, pos, negate):
            """
            Return an extra filter to the queryset so that the results are filtered
            on the appropriate content type.
            """
            if negate:
                return []
            content_type = ContentType.objects.get_for_model(self.model, for_concrete_model=False)
            prefix = "__".join(pieces[:pos + 1])
            return [("%s__%s" % (prefix, self.content_type_field_name),
                    content_type)]

        def bulk_related_objects(self, objs, using=DEFAULT_DB_ALIAS):
            """
            Return all objects related to ``objs`` via this ``GenericRelation``.

            """
            return self.rel.to._base_manager.db_manager(using).filter(**{
                    "%s__pk" % self.content_type_field_name:
                        ContentType.objects.db_manager(using).get_for_model(self.model, for_concrete_model=False).pk,
                    "%s__in" % self.object_id_field_name:
                        [obj.pk for obj in objs]
                    })

        def contribute_to_class(self, cls, name):
            super(generic.GenericRelation, self).contribute_to_class(cls, name)

            # Save a reference to which model this class is on for future use
            self.model = cls

            # Add the descriptor for the m2m relation
            setattr(cls, self.name, ProxyReverseGenericRelatedObjectsDescriptor(self))


    class ProxyReverseGenericRelatedObjectsDescriptor(generic.ReverseGenericRelatedObjectsDescriptor):
        def __get__(self, instance, instance_type=None):
            if instance is None:
                return self

            # Dynamically create a class that subclasses the related model's
            # default manager.
            rel_model = self.field.rel.to
            superclass = rel_model._default_manager.__class__
            RelatedManager = generic.create_generic_related_manager(superclass)

            qn = connection.ops.quote_name
            content_type = ContentType.objects.db_manager(instance._state.db).get_for_model(instance, for_concrete_model=False)

            manager = RelatedManager(
                model=rel_model,
                instance=instance,
                symmetrical=(self.field.rel.symmetrical and instance.__class__ == rel_model),
                source_col_name=qn(self.field.m2m_column_name()),
                target_col_name=qn(self.field.m2m_reverse_name()),
                content_type=content_type,
                content_type_field_name=self.field.content_type_field_name,
                object_id_field_name=self.field.object_id_field_name,
                prefetch_cache_name=self.field.attname,
            )

            return manager


class WidgyGenericForeignKey(ProxyGenericForeignKey):
    def __get__(self, instance, instance_type=None):
        try:
            return super(WidgyGenericForeignKey, self).__get__(instance, instance_type)
        except AttributeError:
            # The model for this content type couldn't be loaded. Use an
            # UnknownWidget instead.
            from widgy.models import UnknownWidget
            ret = UnknownWidget(getattr(instance, self.ct_field), getattr(instance, self.fk_field), instance)
            ret.node = instance
            ret.warn()
            return ret
