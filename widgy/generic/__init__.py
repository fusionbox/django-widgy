from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation


class ProxyGenericForeignKey(GenericForeignKey):
    def __init__(self, *args, **kwargs):
        kwargs['for_concrete_model'] = False
        super(ProxyGenericForeignKey, self).__init__(*args, **kwargs)


class ProxyGenericRelation(GenericRelation):
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
