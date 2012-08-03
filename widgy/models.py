from django.db import models
from django.db.models.signals import post_save
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.template.loader import render_to_string

from mezzanine.pages.models import Page
from mezzanine.core.fields import FileField

from treebeard.mp_tree import MP_Node

from widgy.exceptions import (InvalidTreeMovement, OhHellNo, BadChildRejection,
        BadParentRejection, ParentChildRejection, RootDisplacementError)


class WidgyMixin(models.Model):
    @property
    def root_nodes(self):
        for field in self.get_node_fields():
            yield getattr(self, field.name)

    @classmethod
    def get_node_fields(cls):
        for field in cls._meta.fields:
            if not field.rel:
                continue
            if issubclass(field.rel.to, Node):
                yield field

    @classmethod
    def get_valid_layouts(cls):
        classes = [c for c in Layout.__subclasses__() if c.valid_child_class_of(cls)]
        return classes

    class Meta:
        abstract = True


class ContentPage(Page, WidgyMixin):
    root_node = models.ForeignKey('Node', verbose_name="Widgy Content", blank=True, null=True, on_delete=models.SET_NULL, editable=False)

    class Meta:
        verbose_name = 'Widgy Page'


def exception_to_bool(fn):
    def new(*args, **kwargs):
        try:
            fn(*args, **kwargs)
            return True
        except:
            return False
    return new


class Node(MP_Node):
    content_type = models.ForeignKey(ContentType)
    content_id = models.PositiveIntegerField()
    content = generic.GenericForeignKey('content_type', 'content_id')

    def delete(self, *args, **kwargs):
        content = self.content
        super(Node, self).delete(*args, **kwargs)
        content.delete()

    def to_json(self):
        children = [child.to_json() for child in self.get_children().reverse()]
        json = {
                'url': self.get_api_url(),
                'content': self.content.to_json(),
                'children': children,
                'available_children_url': self.get_available_children_url(),
                }
        parent = self.get_parent()
        if parent:
            json['parent_id'] = parent.get_api_url()

        right = self.get_next_sibling()
        if right:
            json['right_id'] = right.get_api_url()

        return json

    def render(self, *args, **kwargs):
        return self.content.render(*args, **kwargs)

    @models.permalink
    def get_api_url(self):
        return ('widgy.views.node', (), {'node_pk': self.pk})

    @models.permalink
    def get_available_children_url(self):
        return ('widgy.views.recursive_children', (), {'node_pk': self.pk})

    # TODO: fix the error messages
    def reposition(self, right=None, parent=None):
        if not self.content.draggable:
            raise InvalidTreeMovement({'message': "You can't move me"})

        if right:
            if right.is_root():
                raise InvalidTreeMovement({'message': 'You can\'t move the root'})

            right.get_parent().content.validate_relationship(self.content)
            self.move(right, pos='left')
        elif parent:
            parent.content.validate_relationship(self.content)
            self.move(parent, pos='last-child')
        else:
            assert right or parent

    def filter_child_classes(self, classes):
        return set([c for c in classes if exception_to_bool(self.content.validate_relationship)(c)])

    def filter_child_classes_recursive(self, classes):
        allowed_classes = self.filter_child_classes(classes)
        for child in self.get_children():
            allowed_classes.update(child.filter_child_classes(classes))
        return allowed_classes


def call_content_post_save(sender, instance, created, **kwargs):
    if created:
        instance.content.post_create()

post_save.connect(call_content_post_save, sender=Node)


class Content(models.Model):
    _node = generic.GenericRelation(Node,
                               content_type_field='content_type',
                               object_id_field='content_id')

    @property
    def node(self):
        return self._node.all()[0]

    class Meta:
        abstract = True

    def valid_child_of(self, content):
        """
        Given a content instance, will we consent to be adopted by them?
        """
        return self.valid_child_class_of(content)

    @classmethod
    def valid_child_class_of(cls, content):
        """
        Given a content instance, does our class consent to be adopted by them?
        """
        return True

    def valid_parent_of_class(self, cls):
        """
        Given a content class, can it be _added_ as our child?
        Note: this does not apply to _existing_ children (adoption)
        """
        return self.accepting_children

    def valid_parent_of_instance(self, content):
        """
        Given a content instance, can we adopt them?
        """
        return self.valid_parent_of_class(type(content))

    draggable = True
    deletable = True
    accepting_children = False

    def validate_relationship(self, child):
        parent = self
        if isinstance(child, Content):
            bad_parent = not child.valid_child_of(parent)
            bad_child = not parent.valid_parent_of_instance(child)
        else:
            bad_parent = not child.valid_child_class_of(parent)
            bad_child = not parent.valid_parent_of_class(child)

        if bad_parent and bad_child:
            raise OhHellNo
        elif bad_parent:
            raise BadParentRejection
        elif bad_child:
            raise BadChildRejection

    def add_child(self, cls, **kwargs):
        obj = cls.objects.create(**kwargs)

        try:
            self.validate_relationship(obj)
        except ParentChildRejection:
            obj.delete()
            raise

        self.node.add_child(
                content=obj
                )
        return obj

    def add_sibling(self, cls, **kwargs):
        if self.node.is_root():
            raise RootDisplacementError({'message': 'You can\'t put things next to me'})

        obj = cls.objects.create(**kwargs)
        parent = self.node.get_parent().content

        try:
            parent.validate_relationship(obj)
        except ParentChildRejection:
            obj.delete()
            raise

        self.node.add_sibling(
                content=obj,
                pos='left'
                )
        return obj

    @classmethod
    def add_root(cls, **kwargs):
        obj = cls.objects.create(**kwargs)
        Node.add_root(
                content=obj
                )
        return obj

    def post_create(self):
        """
        Hook for custom code which needs to be run after creation.  Since the
        `Node` must be created after the widget, any tree based actions
        have to happen after the save event has finished.
        """
        pass

    def to_json(self):
        return {
                'url': self.get_api_url(),
                '__class__': "%s.%s" % (self._meta.app_label, self._meta.module_name),
                'model': self._meta.module_name,
                'object_name': self._meta.object_name,
                'draggable': self.draggable,
                'deletable': self.deletable,
                'accepting_children': self.accepting_children,
                }

    @models.permalink
    def get_api_url(self):
        return ('widgy.views.content', (), {
            'object_name': self._meta.module_name,
            'app_label': self._meta.app_label,
            'object_pk': self.pk})

    def get_templates(self):
        templates = (
                'widgy/{module_name}.html'.format(module_name=self._meta.module_name),
                )
        return templates

    def render(self, context):
        context.update({'content': self})
        rendered_content = render_to_string(self.get_templates(), context)
        context.pop()
        return rendered_content

    @classmethod
    def class_to_json(cls):
        return {
                '__class__': "%s.%s" % (cls._meta.app_label, cls._meta.module_name),
                'title': cls._meta.verbose_name.title(),
                }

    @classmethod
    def all_concrete_subclasses(cls):
        classes = set(c for c in cls.__subclasses__() if not c._meta.abstract)
        for c in cls.__subclasses__():
            classes.update(c.all_concrete_subclasses())
        return classes


class Bucket(Content):
    title = models.CharField(max_length=255)
    draggable = models.BooleanField(default=True)
    deletable = models.BooleanField(default=True)

    accepting_children = True

    def valid_parent_of_class(self, cls):
        return not issubclass(cls, Bucket)

    def to_json(self):
        json = super(Bucket, self).to_json()
        json['title'] = self.title
        return json


class Layout(Content):
    """
    Base class for all layouts.
    """
    class Meta:
        abstract = True

    draggable = False
    deletable = False

    def valid_parent_of_instance(self, content):
        return any(isinstance(content, bucket_meta[1]) for bucket_meta in self.buckets) and\
                (content.id in [i.content.id for i in self.node.get_children()] or
                        len(self.node.get_children()) < len(self.buckets))

    def valid_parent_of_class(self, cls):
        return any(issubclass(cls, bucket_meta[1]) for bucket_meta in self.buckets) and\
                len(self.node.get_children()) < len(self.buckets)

    @classmethod
    def valid_child_class_of(cls, content):
        return isinstance(content, ContentPage) or issubclass(content, Page)

    def post_create(self):
        for bucket_title, bucket_class, args, kwargs in self.buckets:
            self.add_child(bucket_class, title=bucket_title, *args, **kwargs)


class TwoColumnLayout(Layout):
    """
    On creation, creates a left and right bucket.
    """

    buckets = [
            ('left', Bucket, (), {'draggable': False, 'deletable': False}),
            ('right', Bucket, (), {'draggable': False, 'deletable': False}),
            ]

    @property
    def left_bucket(self):
        return self.node.get_children()[0]

    @property
    def right_bucket(self):
        return self.node.get_children()[1]

    class Meta:
        verbose_name = 'Two Column Layout'


class TextContent(Content):
    content = models.TextField()

    def to_json(self):
        json = super(TextContent, self).to_json()
        json['content'] = self.content
        return json


class ImageContent(Content):
    image = FileField(max_length=255, format="Image")

    def to_json(self):
        json = super(ImageContent, self).to_json()
        if self.image:
            json['image'] = self.image.path
            json['image_url'] = self.image.url
        return json
