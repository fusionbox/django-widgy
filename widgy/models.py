from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.template import Context
from django.template.loader import render_to_string

from mezzanine.pages.models import Page

from treebeard.mp_tree import MP_Node


class ContentPage(Page):
    root_node = models.ForeignKey('Node', null=True)

    def to_json(self):
        return {
                'id': self.id,
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

    def to_json(self):
        children = [child.to_json() for child in self.get_children()]
        return {
                'id': self.id,
                'content': self.content.to_json(),
                'children': children,
                }

    def render(self):
        return self.content.render()

    @staticmethod
    def validate_parent_child(parent, child):
        return parent.content.valid_parent_of(child) and child.content.valid_child_of(parent)



class Content(models.Model):
    _node = generic.GenericRelation(Node,
                               content_type_field='content_type',
                               object_id_field='content_id')

    @property
    def node(self):
        return self._node.all()[0]

    class Meta:
        abstract = True

    def valid_child_of(self, content_class):
        return True

    def valid_parent_of(self, content_class):
        return False

    def add_child(self, cls, **kwargs):
        obj = cls.objects.create(**kwargs)
        node = self.node.add_child(
                content=obj
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
                'id': self.id,
                'model': self._meta.module_name,
                'object_name': self._meta.object_name,
                }


class Bucket(Content):
    title = models.CharField(max_length=255)

    def valid_parent_of(self, content_class):
        return True

    def to_json(self):
        json = super(Bucket, self).to_json()
        json['title'] = self.title
        return json

    def render(self):
        return render_to_string('widgy/bucket.html', {
            'nodes': self.node.get_children(),
            })


class TwoColumnLayout(Content):
    """
    On creation, creates a left and right bucket.
    """

    buckets = {
            'left': Bucket,
            'right': Bucket,
            }

    def valid_child_of(self, content_class):
        return isinstance(content_class, ContentPage)

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

    def render(self):
        return render_to_string('widgy/two_column_layout.html', {
            'left_bucket': self.left_bucket.content,
            'right_bucket': self.right_bucket.content,
            })


class TextContent(Content):
    content = models.TextField()

    def to_json(self):
        json = super(TextContent, self).to_json()
        json['content'] = self.content
        return json

    def render(self):
        return render_to_string('widgy/text_content.html', {
            'content': self.content,
            })
