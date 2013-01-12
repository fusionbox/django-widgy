from django.db import models
from django.conf import settings

from widgy.models import Content
from widgy.db.fields import WidgyField
from widgy.contrib.page_builder.db.fields import MarkdownField
from widgy.utils import path_generator
from widgy import registry


class PageBuilderContent(Content):
    """
    Base class for all page builder content models.
    """
    def get_render_templates(self, context):
        templates = list(super(PageBuilderContent, self).get_render_templates(context))
        template_path = path_generator(u'widgy/')
        for cls in filter(lambda c: issubclass(c, Content), self.__class__.__mro__):
            templates.extend([
                template_path(
                    cls._meta.module_name
                ),
            ])

        return templates

    class Meta:
        abstract = True


class Layout(PageBuilderContent):
    """
    Base class for all layouts.
    """
    class Meta:
        abstract = True

    draggable = False
    deletable = False
    editable = True

    component_name = 'layout'

    default_children = tuple()

    def post_create(self, site):
        for cls, args, kwargs in self.default_children:
            self.add_child(site, cls, *args, **kwargs)

    @property
    def max_number_of_children(self):
        return len(self.default_children)

    def valid_parent_of(self, cls, obj=None):
        if obj and obj in self.children:
            return True
        return (any(issubclass(cls, bucket_meta[0]) for bucket_meta in self.default_children) and
                super(Layout, self).valid_parent_of(cls, obj))

    @classmethod
    def valid_child_of(cls, content, obj=None):
        return False


class Bucket(PageBuilderContent):
    draggable = False
    deletable = False

    component_name = 'bucket'

    class Meta:
        abstract = True


class Widget(PageBuilderContent):
    component_name = 'widget'

    class Meta:
        abstract = True

    @property
    def preview_templates(self):
        return (
            'widgy/%s/widget.html' % self.class_name,
            'widgy/widget.html',
        )


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
    max_number_of_children = 0

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
        return issubclass(cls, Section) and super(Accordion, self).valid_parent_of(cls, obj)

registry.register(Accordion)


class Section(Widget):
    title = models.CharField(max_length=1023)

    @classmethod
    def valid_child_of(cls, parent, obj=None):
        return isinstance(parent, Accordion)

registry.register(Section)
