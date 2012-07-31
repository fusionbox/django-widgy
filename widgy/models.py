from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.template.loader import render_to_string

from mezzanine.pages.models import Page

from treebeard.mp_tree import MP_Node


class ContentPage(Page):
    root_node = models.ForeignKey('Node', null=True, on_delete=models.SET_NULL)

    def to_json(self):
        return {
                'title': self.title,
                'root_node': self.root_node.to_json(),
                }

    def render(self):
        return render_to_string('widgy/content_page.html', {
            'title': self.title,
            'root_node': self.root_node,
            })


class Node(MP_Node):
    content_type = models.ForeignKey(ContentType)
    content_id = models.PositiveIntegerField()
    content = generic.GenericForeignKey('content_type', 'content_id')

    def save(self, *args, **kwargs):
        new = not self.id
        super(Node, self).save(*args, **kwargs)
        if new:
            self.content.post_create()

    def delete(self, *args, **kwargs):
        self.content.delete()

    def to_json(self):
        children = [child.to_json() for child in self.get_children().reverse()]
        json = {
                'url': self.get_api_url(),
                'content': self.content.to_json(),
                'children': children,
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


    # TODO: fix the error messages
    def reposition(self, right=None, parent=None):
        if right:
            if right.is_root():
                raise InvalidTreeMovement({'message': 'You can\'t move the root'})

            right.get_parent().content.validate_relationship(self.content)
            self.move(right, pos='left')
        elif parent:
            parent.content.validate_relationship(self.content)
            self.move(parent, pos='first-child')
        else:
            assert right or parent


class InvalidTreeMovement(ValidationError):
    pass

class RootDisplacementError(InvalidTreeMovement):
    pass

class ParentChildRejection(InvalidTreeMovement):
    pass


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
        return True

    def valid_parent_of(self, content):
        return self.valid_parent_of_class(type(content)) and\
                self.valid_parent_of_instance(content)

    def valid_parent_of_instance(self, content):
        return False

    def valid_parent_of_class(self, cls):
        return False

    def validate_relationship(self, child):
        if not self.valid_parent_of(child):
            raise ParentChildRejection({'message': 'You can\'t put that in me.'})

        if not child.valid_child_of(self):
            raise ParentChildRejection({'message': 'You can\'t put me in that.'})

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
        node = Node.add_root(
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
                '__module_name__': self._meta.module_name,
                'model': self._meta.module_name,
                'object_name': self._meta.object_name,
                }

    @models.permalink
    def get_api_url(self):
        return ('widgy.views.content', (), {'object_name': self._meta.module_name, 'object_pk': self.pk})

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


class Bucket(Content):
    title = models.CharField(max_length=255)

    def valid_parent_of_instance(self, content):
        return True

    def valid_parent_of_class(self, cls):
        return True

    def to_json(self):
        json = super(Bucket, self).to_json()
        json['title'] = self.title
        return json


class TwoColumnLayout(Content):
    """
    On creation, creates a left and right bucket.
    """

    buckets = {
            'left': Bucket,
            'right': Bucket,
            }

    def valid_child_of(self, content):
        return isinstance(content, ContentPage)

    def valid_parent_of_instance(self, content):
        return content.id in [i.content.id for i in self.node.get_children()] or len(self.node.get_children()) < 2

    def valid_parent_of_class(self, cls):
        return issubclass(cls, Bucket)

    def post_create(self):
        for bucket_title, bucket_class in self.buckets.iteritems():
            bucket = self.add_child(bucket_class,
                    title=bucket_title,
                    )

    @property
    def left_bucket(self):
        return [i for i in self.node.get_children() if i.content.title=='left'][0]

    @property
    def right_bucket(self):
        return [i for i in self.node.get_children() if i.content.title=='right'][0]


class TextContent(Content):
    content = models.TextField()

    def to_json(self):
        json = super(TextContent, self).to_json()
        json['content'] = self.content
        return json
