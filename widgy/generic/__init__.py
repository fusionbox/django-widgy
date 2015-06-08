import django
from django.contrib.contenttypes import generic
from django.db import DEFAULT_DB_ALIAS, connection
from django.contrib.contenttypes.models import ContentType

try:
    from south.modelsinspector import add_ignored_fields
except ImportError:  # South not installed.
    pass
else:
    add_ignored_fields(["^widgy\.generic\.ProxyGenericRelation",
                        "^widgy\.generic\.ProxyGenericForeignKey",
                        "^widgy\.generic\.WidgyGenericForeignKey"])


class ProxyGenericForeignKey(generic.GenericForeignKey):
    def __init__(self, *args, **kwargs):
        kwargs['for_concrete_model'] = False
        super(ProxyGenericForeignKey, self).__init__(*args, **kwargs)


class ProxyGenericRelation(generic.GenericRelation):
    def __init__(self, *args, **kwargs):
        kwargs['for_concrete_model'] = False
        super(ProxyGenericRelation, self).__init__(*args, **kwargs)


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
