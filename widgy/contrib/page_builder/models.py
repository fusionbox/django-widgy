from django.db import models
from django.conf import settings

from widgy.models import Content
from widgy.models.mixins import StrictDefaultChildrenMixin
from widgy.db.fields import WidgyField
from widgy.contrib.page_builder.db.fields import MarkdownField
from widgy import registry


class PageBuilderContent(Content):
    """
    Base class for all page builder content models.
    """
    class Meta:
        abstract = True


class Layout(StrictDefaultChildrenMixin, PageBuilderContent):
    """
    Base class for all layouts.
    """
    class Meta:
        abstract = True

    draggable = False
    deletable = False
    editable = True

    component_name = 'layout'

    @classmethod
    def valid_child_of(cls, content, obj=None):
        return False


class Bucket(PageBuilderContent):
    draggable = False
    deletable = False
    accepting_children = True

    component_name = 'bucket'

    class Meta:
        abstract = True


class Widget(PageBuilderContent):
    component_name = 'widget'

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


class Markdown(Widget):
    content = MarkdownField(blank=True)
    rendered = models.TextField(editable=False)

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


class CalloutWidget(Widget):
    callout = models.ForeignKey(Callout, null=True, blank=True)

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


class Section(Widget):
    accepting_children = True

    title = models.CharField(max_length=1023)

    @classmethod
    def valid_child_of(cls, parent, obj=None):
        return isinstance(parent, Accordion)

registry.register(Section)
