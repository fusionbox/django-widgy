"""
Collection of widgy classes for building a content-driven website.
"""
from django.db import models
from widgy.forms import WidgyField
from widgy.models import Content
from mezzanine.core.fields import FileField
from mezzanine.pages.models import Page


class ContentPage(Page):
    root_node = WidgyField(
        verbose_name='Widgy Content',
        root_choices=(
            'TwoColumnLayout',
        ),
    )

    class Meta:
        verbose_name = 'Widgy Page'
        db_table = 'widgy_cms_contentpage'


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

    class Meta:
        db_table = 'widgy_cms_bucket'


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

    class Meta:
        verbose_name = 'Two Column Layout'
        db_table = 'widgy_cms_twocolumnlayout'

    @property
    def left_bucket(self):
        return self.node.get_children()[0]

    @property
    def right_bucket(self):
        return self.node.get_children()[1]


class TextContent(Content):
    content = models.TextField()

    class Meta:
        verbose_name = 'Two Column Layout'
        db_table = 'widgy_cms_textcontent'

    def to_json(self):
        json = super(TextContent, self).to_json()
        json['content'] = self.content
        return json


class CommonCallout(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True, default='')
    button_text = models.CharField(max_length=255, blank=True, default='')
    button_href = models.CharField(max_length=255, blank=True, default='')


class CommonCalloutContent(Content):
    inherits_from = models.ForeignKey(CommonCallout, null=True, blank=True)

    class Meta:
        verbose_name = 'Common Callout Content'
        db_table = 'widgy_cms_commoncalloutcontent'


class ImageContent(Content):
    image = FileField(max_length=255, format="Image")


    def to_json(self):
        json = super(ImageContent, self).to_json()
        if self.image:
            json['image'] = self.image.path
            json['image_url'] = self.image.url
        return json
