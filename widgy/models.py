from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.template import Context
from django.template.loader import get_template

from mezzanine.pages.models import Page

from treebeard.mp_tree import MP_Node


class ContentPage(Page):
    root_widget = models.ForeignKey('WidgetNode', null=True)

    def to_json(self):
        return {
                'id': self.id,
                'title': self.title,
                'root_node': self.root_widget.to_json(),
                }

    def render(self):
        t = get_template('widgy/content_page.html')
        return t.render(Context({
            'title': self.title,
            'root_node': self.root_widget,
            }))


class WidgetNode(MP_Node):
    data_type = models.ForeignKey(ContentType)
    data_id = models.PositiveIntegerField()
    data = generic.GenericForeignKey('data_type', 'data_id')

    def save(self, *args, **kwargs):
        new = not self.id
        super(WidgetNode, self).save(*args, **kwargs)
        if new:
            self.data.post_create()

    def to_json(self):
        return {
                'id': self.id,
                'content': self.data.to_json(),
                }

    def render(self):
        return self.data.render()


class WidgetData(models.Model):
    _widget = generic.GenericRelation(WidgetNode,
                               content_type_field='data_type',
                               object_id_field='data_id')

    @property
    def node(self):
        return self._widget.all()[0]

    class Meta:
        abstract = True

    def valid_child_of(self, widget_class):
        return True

    def valid_parent_of(self, widget_class):
        return False

    def add_child(self, cls, **kwargs):
        obj = cls.objects.create(**kwargs)
        node = self.node.add_child(
                data=obj
                )
        return obj

    @classmethod
    def add_root(cls, **kwargs):
        obj = cls.objects.create(**kwargs)
        node = WidgetNode.add_root(
                data=obj
                )
        return obj

    def post_create(self):
        """
        Hook for custom code which needs to be run after creation.  Since the
        `WidgetNode` must be created after the widget, any tree based actions
        have to happen after the save event has finished.
        """
        pass

    def to_json(self):
        children = [child.to_json() for child in self.node.get_children()]
        return {
                'id': self.id,
                'model': self._meta.object_name,
                'children': children,
                }


class Bucket(WidgetData):
    title = models.CharField(max_length=255)

    def valid_parent_of(self, widget_class):
        return True

    def to_json(self):
        json = super(Bucket, self).to_json()
        json['title'] = self.title
        return json

    def render(self):
        t = get_template('widgy/bucket.html')
        return t.render(Context({
            'nodes': self.node.get_children(),
            }))


class TwoColumnLayout(WidgetData):
    """
    On creation, creates a left and right bucket.
    """

    buckets = {
            'left': Bucket,
            'right': Bucket,
            }

    def valid_child_of(self, widget_class):
        return isinstance(widget_class, ContentPage)

    def post_create(self):
        for bucket_title, bucket_class in self.buckets.iteritems():
            bucket = self.add_child(bucket_class,
                    title=bucket_title,
                    )

    @property
    def left_bucket(self):
        return [i for i in self.node.get_children() if i.data.title=='left'][0]

    @property
    def right_bucket(self):
        return [i for i in self.node.get_children() if i.data.title=='right'][0]

    def render(self):
        t = get_template('widgy/two_column_layout.html')
        return t.render(Context({
            'left_bucket': self.left_bucket.data,
            'right_bucket': self.right_bucket.data,
            }))


class TextContent(WidgetData):
    content = models.TextField()

    def to_json(self):
        json = super(TextContent, self).to_json()
        json['content'] = self.content
        return json

    def render(self):
        t = get_template('widgy/text_content.html')
        return t.render(Context({
            'content': self.content,
            }))
