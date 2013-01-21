import os

from django import forms
from django.db import models
from django.conf import settings

from filer.fields.file import FilerFileField
from filer.models.filemodels import File

from widgy.models import Content
from widgy.models.mixins import StrictDefaultChildrenMixin
from widgy.db.fields import WidgyField
from widgy.contrib.page_builder.db.fields import MarkdownField
from widgy import registry


class Layout(StrictDefaultChildrenMixin, Content):
    """
    Base class for all layouts.
    """
    class Meta:
        abstract = True

    draggable = False
    deletable = False

    @classmethod
    def valid_child_of(cls, content, obj=None):
        return False


class Bucket(Content):
    draggable = False
    deletable = False
    accepting_children = True

    class Meta:
        abstract = True


class MainContent(Bucket):
    def valid_parent_of(self, cls, obj=None):
        return not issubclass(cls, (MainContent, Sidebar))

    @classmethod
    def valid_child_of(cls, parent, obj=None):
        return isinstance(parent, Layout)

registry.register(MainContent)


class Sidebar(Bucket):
    pop_out = 1

    def to_json(self, site):
        from datetime import datetime
        json = super(Sidebar, self).to_json(site)
        json['content'] = str(datetime.now())
        return json

    def valid_parent_of(self, cls, obj=None):
        return not issubclass(cls, (MainContent, Sidebar))

    @classmethod
    def valid_child_of(cls, parent, obj=None):
        return isinstance(parent, Layout)

registry.register(Sidebar)


class DefaultLayout(Layout):
    """
    On creation, creates a left and right bucket.
    """
    class Meta:
        verbose_name = 'Default layout'

    default_children = [
        (MainContent, (), {}),
        (Sidebar, (), {}),
    ]

registry.register(DefaultLayout)


class Markdown(Content):
    content = MarkdownField(blank=True)
    rendered = models.TextField(editable=False)

    editable = True
    component_name = 'markdown'

registry.register(Markdown)


class CalloutBucket(Bucket):
    @classmethod
    def valid_child_of(cls, parent, obj=None):
        return False

    def valid_parent_of(self, cls, obj=None):
        return issubclass(cls, (Markdown,))

registry.register(CalloutBucket)


class Callout(models.Model):
    name = models.CharField(max_length=255)
    root_node = WidgyField(
        site=settings.WIDGY_MEZZANINE_SITE,
        verbose_name='Widgy Content',
        root_choices=(
            'CalloutBucket',
        ))

    def __unicode__(self):
        return self.name


class CalloutWidget(Content):
    callout = models.ForeignKey(Callout, null=True, blank=True)

    editable = True

    @classmethod
    def valid_child_of(cls, parent, obj=None):
        return isinstance(parent, Sidebar)

registry.register(CalloutWidget)


class Accordion(Bucket):
    draggable = True
    deletable = True

    def valid_parent_of(self, cls, obj=None):
        return issubclass(cls, Section)

registry.register(Accordion)


class Section(Content):
    title = models.CharField(max_length=1023)

    editable = True
    accepting_children = True

    @classmethod
    def valid_child_of(cls, parent, obj=None):
        return isinstance(parent, Accordion)

registry.register(Section)


def validate_image(file_pk):
    file = File.objects.get(pk=file_pk)
    iext = os.path.splitext(file.file.path)[1].lower()
    if not iext in ['.jpg', '.jpeg', '.png', '.gif']:
        raise forms.ValidationError('File type must be jpg, png, or gif')
    return file_pk


class Image(Content):
    editable = True

    # What should happen on_delete.  Set to models.PROTECT so this is harder to
    # ignore and forget about.
    image = FilerFileField(null=True, blank=True,
                           validators=[validate_image],
                           related_name='image_widgets',
                           on_delete=models.PROTECT)

registry.register(Image)
