from django.db import models

from widgy.models import Content
from widgy.db.fields import WidgyField
from widgy.contrib.page_builder.db.fields import MarkdownField
from widgy.utils import path_generator


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

    default_children = tuple()

    def post_create(self, site):
        for cls, args, kwargs in self.default_children:
            self.add_child(site, cls, *args, **kwargs)

    def valid_parent_of_instance(self, content):
        return any(isinstance(content, bucket_meta[0]) for bucket_meta in self.default_children) and\
                (content.id in [i.content.id for i in self.node.get_children()] or
                        len(self.node.get_children()) < len(self.default_children))

    def valid_parent_of_class(self, cls):
        return any(issubclass(cls, bucket_meta[0]) for bucket_meta in self.default_children) and\
                len(self.node.get_children()) < len(self.default_children)

    @classmethod
    def valid_child_class_of(cls, content):
        return False


class Bucket(PageBuilderContent):
    draggable = False
    deletable = False
    accepting_children = True

    component_name = 'bucket'

    class Meta:
        abstract = True

    def valid_parent_of_class(self, cls):
        return True


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
    def valid_parent_of_class(self, cls):
        return not issubclass(cls, MainContent) and not issubclass(cls, Sidebar)

    @classmethod
    def valid_child_class_of(cls, parent):
        return isinstance(parent, Layout)


class Sidebar(Bucket):
    pop_out = 1

    def to_json(self, site):
        from datetime import datetime
        json = super(Sidebar, self).to_json(site)
        json['content'] = str(datetime.now())
        return json

    def valid_parent_of_class(self, cls):
        return not issubclass(cls, MainContent) and not issubclass(cls, Sidebar)

    @classmethod
    def valid_child_class_of(cls, parent):
        return isinstance(parent, Layout)


class DefaultLayout(Layout):
    """
    On creation, creates a left and right bucket.
    """

    deletable = False
    editable = True
    component_name = 'layout'

    class Meta:
        verbose_name = 'Default layout'

    default_children = [
        (MainContent, (), {}),
        (Sidebar, (), {}),
    ]


class Markdown(Widget):
    content = MarkdownField(blank=True)
    rendered = models.TextField(editable=False)

    component_name = 'markdown'


class CalloutBucket(Bucket):
    @classmethod
    def valid_child_class_of(cls, parent):
        return False

    def valid_parent_of_class(self, cls):
        return cls in (Markdown,)


class Callout(models.Model):
    name = models.CharField(max_length=255)
    root_node = WidgyField(
        verbose_name='Widgy Content',
        root_choices=(
            'CalloutBucket',
        ))

    def __unicode__(self):
        return self.name


class CalloutWidget(Widget):
    callout = models.ForeignKey(Callout, null=True, blank=True)

    @classmethod
    def valid_child_class_of(cls, parent):
        return isinstance(parent, Sidebar)


class Accordion(Bucket):
    draggable = True
    deletable = True

    def valid_parent_of_class(self, cls):
        return issubclass(cls, Section)


class Section(Widget):
    accepting_children = True

    title = models.CharField(max_length=1023)

    @classmethod
    def valid_child_class_of(cls, parent):
        return isinstance(parent, Accordion)
