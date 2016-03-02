import six

from django.db import models
from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.utils.functional import SimpleLazyObject

from django.contrib.contenttypes.models import ContentType
from widgy.utils import fancy_import, update_context

try:
    from south.modelsinspector import add_introspection_rules
except ImportError:  # South not installed
    pass
else:
    add_introspection_rules([], ["^widgy\.db.fields\.WidgyField"])
    add_introspection_rules([], ["^widgy\.db.fields\.VersionedWidgyField"])

try:
    from django.db.models.fields.related import ForwardManyToOneDescriptor
except ImportError:
    # django < 1.9
    from django.db.models.fields.related import ReverseSingleRelatedObjectDescriptor as ForwardManyToOneDescriptor



def get_site(site):
    if isinstance(site, six.string_types):
        return fancy_import(site)
    else:
        return site


class WidgyFieldObjectDescriptor(ForwardManyToOneDescriptor):
    """
    .. note::
        we need to transport the ContentType of the Node all the way to
        ``pre_save``, without saving an instance of the node, because we don't
        know if the rest of the model is valid yet.
    """
    def __set__(self, instance, value):
        if isinstance(value, ContentType):
            setattr(instance, self.field.pre_save_ct_field_name, value)
        else:
            super(WidgyFieldObjectDescriptor, self).__set__(instance, value)
            if hasattr(instance, self.field.pre_save_ct_field_name):
                delattr(instance, self.field.pre_save_ct_field_name)


class WidgyField(models.ForeignKey):
    """
    Model field that inherits from ``models.ForeignKey``.  Contains validation
    and context switching that is needed for Widgy fields.

    A WidgyField can be assigned a ContentType instance in order to create a
    new root node of that content type. ::

        my_content_type = ContentType.objects.get_for_model(Layout)
        my_model = MyModel(
            root_node=my_content_type
        )
    """
    def __init__(self, site=None, to=None, root_choices=None, **kwargs):
        if to is None:
            to = 'widgy.Node'

        self.root_choices = root_choices

        self.site = get_site(site)

        super(WidgyField, self).__init__(to, **kwargs)

    def contribute_to_class(self, cls, name):
        """

        .. note:: we need to use WidgyFieldObjectDescriptor instead of
            ``ReverseSingleRelatedObjectDescriptor`` because of the modifications
            to __set__.
        """
        super(WidgyField, self).contribute_to_class(cls, name)
        setattr(cls, self.name, WidgyFieldObjectDescriptor(self))

    @property
    def pre_save_ct_field_name(self):
        return '_widgy_field_pre_save_ct_{0}'.format(self.name)

    def add_root(self, model_instance, root_content_kwargs={}):
        # This is a weird API. It would be nicer to take the content class of
        # the new root node, but add_root is a public interface
        # (django-widgy-blog is using it).
        content_type = getattr(model_instance, self.pre_save_ct_field_name)
        return content_type.model_class().add_root(self.site, **root_content_kwargs).node

    def pre_save(self, model_instance, add):
        """
        When adding a new root, we might be passed a ContentType that we need
        to turn into a root node. Relies on WidgyFieldObjectDescriptor to set
        the content type in pre_save_ct_field_name.
        """
        if hasattr(model_instance, self.pre_save_ct_field_name):
            node = self.add_root(model_instance)
            setattr(model_instance, self.name, node)
            setattr(model_instance, self.attname, node.pk)

        return super(WidgyField, self).pre_save(model_instance, add)

    def formfield(self, **kwargs):
        from widgy.forms import WidgyFormField

        defaults = {
            'form_class': WidgyFormField,
            'queryset': SimpleLazyObject(lambda: self.get_layout_contenttypes(self.root_choices)),
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
            return getattr(apps.get_app_config(app_label).models_module, model_name)

        layouts = tuple(map(normalize, layouts))
        classes = (cls for cls in self.site.get_all_content_classes()
                   if self.site.valid_root_of(self, cls, layouts))

        # This method must return a queryset, because it is used as
        # choices for a ModelChoiceField.
        #
        # If you are having trouble running tests because of this line,
        # do not create WidgyFormMixin subclasses at the root level, the
        # test databases haven't been set up yet, but we try to query
        # the ContentType table.
        return ContentType.objects.filter(pk__in=[
            ct.pk for ct in ContentType.objects.get_for_models(
                for_concrete_models=False,
                *classes
            ).values()])

    def get_render_node(self, model_instance, context):
        return getattr(model_instance, self.name)

    def render(self, model_instance, context=None, node=None):
        root_node = node or self.get_render_node(model_instance, context)
        if not root_node:
            return 'no content'

        root_node.prefetch_tree()
        env = {
            'widgy': {
                'site': self.site,
                'owner': model_instance,
                'root_node': root_node,
                'parent': context and context.get('widgy'),
            },
        }
        with update_context(context, env) as context:
            return root_node.render(context)

    def validate(self, value, model_instance):
        # `value` is our root node's pk. If we're currently creating
        # the root node, it isn't saved so it can't have a pk. The base
        # field's validate will fail, even though pre_save will actually
        # create a node and set the fk field.
        if value is None and not self.blank and hasattr(model_instance, self.pre_save_ct_field_name):
            return
        else:
            return super(WidgyField, self).validate(value, model_instance)


class VersionedWidgyField(WidgyField):
    def __init__(self, site=None, to=None, root_choices=None, **kwargs):
        if to is None:
            to = get_site(site).get_version_tracker_model()
        super(VersionedWidgyField, self).__init__(site, to, root_choices, **kwargs)

    def add_root(self, model_instance, root_content_kwargs={}):
        VersionTracker = self.site.get_version_tracker_model()
        node = super(VersionedWidgyField, self).add_root(model_instance, root_content_kwargs)
        version_tracker = VersionTracker.objects.create(
            working_copy=node
        )
        return version_tracker

    def formfield(self, **kwargs):
        from widgy.forms import VersionedWidgyFormField
        return super(VersionedWidgyField, self).formfield(
            form_class=VersionedWidgyFormField,
            **kwargs)

    def get_render_node(self, model_instance, context):
        version_tracker = getattr(model_instance, self.name)
        if version_tracker:
            node = version_tracker.get_published_node(context and context.get('request'))
            if node is None:
                node = version_tracker.working_copy
            return node
        else:
            return None
