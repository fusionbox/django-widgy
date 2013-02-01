import os

from django import forms
from django.db import models
from django.conf import settings

from filer.fields.file import FilerFileField
from filer.models.filemodels import File

from widgy.models import Content
from widgy.models.mixins import StrictDefaultChildrenMixin, InvisibleMixin
from widgy.db.fields import WidgyField
from widgy.contrib.page_builder.db.fields import MarkdownField, VideoField
import widgy


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


@widgy.register
class MainContent(Bucket):
    def valid_parent_of(self, cls, obj=None):
        return not issubclass(cls, (MainContent, Sidebar))

    @classmethod
    def valid_child_of(cls, parent, obj=None):
        return isinstance(parent, Layout)


@widgy.register
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


@widgy.register
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


@widgy.register
class Markdown(Content):
    content = MarkdownField(blank=True)
    rendered = models.TextField(editable=False)

    editable = True
    component_name = 'markdown'


@widgy.register
class CalloutBucket(Bucket):
    @classmethod
    def valid_child_of(cls, parent, obj=None):
        return False

    def valid_parent_of(self, cls, obj=None):
        return issubclass(cls, (Markdown,))



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


@widgy.register
class CalloutWidget(Content):
    callout = models.ForeignKey(Callout, null=True, blank=True)

    editable = True

    @classmethod
    def valid_child_of(cls, parent, obj=None):
        return isinstance(parent, Sidebar)


@widgy.register
class Accordion(Bucket):
    draggable = True
    deletable = True

    def valid_parent_of(self, cls, obj=None):
        return issubclass(cls, Section)


@widgy.register
class Section(Content):
    title = models.CharField(max_length=1023)

    editable = True
    accepting_children = True

    @classmethod
    def valid_child_of(cls, parent, obj=None):
        return isinstance(parent, Accordion)

def validate_image(file_pk):
    file = File.objects.get(pk=file_pk)
    iext = os.path.splitext(file.file.path)[1].lower()
    if not iext in ['.jpg', '.jpeg', '.png', '.gif']:
        raise forms.ValidationError('File type must be jpg, png, or gif')
    return file_pk


@widgy.register
class Image(Content):
    editable = True

    # What should happen on_delete.  Set to models.PROTECT so this is harder to
    # ignore and forget about.
    image = FilerFileField(null=True, blank=True,
                           validators=[validate_image],
                           related_name='image_widgets',
                           on_delete=models.PROTECT)


class TableElement(Content):
    class Meta:
        abstract = True

    @property
    def table(self):
        for i in reversed(self.get_ancestors()):
            if isinstance(i, Table):
                return i
        assert False, "This TableElement isn't in a table?!?"

    def get_siblings(self):
        return list(self.get_parent().get_children())

    @property
    def sibling_index(self):
        return self.get_siblings().index(self)


@widgy.register
class TableRow(TableElement):
    tag_name = 'tr'

    @classmethod
    def valid_child_of(cls, parent, obj=None):
        return isinstance(parent, TableBody)

    def valid_parent_of(self, cls, obj=None):
        return issubclass(cls, TableData)

    def post_create(self, site):
        for column in self.table.header.get_children():
            self.add_child(site, TableData)


@widgy.register
class TableHeaderData(TableElement):
    tag_name = 'th'

    accepting_children = True
    draggable = True
    deletable = True

    class Meta:
        verbose_name = 'column'

    @classmethod
    def valid_child_of(cls, parent, obj=None):
        if obj and obj.get_parent():
            # we can't be moved to another table
            return obj in parent.get_children()
        else:
            return isinstance(parent, TableHeader)

    def post_create(self, site):
        right = self.get_next_sibling()
        if right:
            for d in self.table.cells_at_index(right.sibling_index - 1):
                d.add_sibling(site, TableData)
        else:
            for row in self.table.body.get_children():
                row.add_child(site, TableData)

    def pre_delete(self):
        for i in self.table.cells_at_index(self.sibling_index):
            i.node.delete()

    def reposition(self, site, right=None, parent=None):
        # we must always stay in the same table
        assert not parent or self.get_parent() == parent

        prev_index = self.sibling_index
        right_index = right and right.sibling_index

        super(TableHeaderData, self).reposition(site, right, parent)

        if right:
            new_rights = self.table.cells_at_index(right_index)
        else:
            new_rights = [None] * len(self.get_siblings())

        for (i, new_right) in zip(self.table.cells_at_index(prev_index), new_rights):
            i.reposition(site, new_right, i.get_parent())


@widgy.register
class TableData(TableElement):
    tag_name = 'td'

    accepting_children = True
    draggable = False
    deletable = False

    @classmethod
    def valid_child_of(cls, parent, obj=None):
        # this is kind of a hack -- we are valid children of TableRow, but we
        # can't be added from the shelf
        if obj:
            return isinstance(parent, TableRow)
        else:
            return False


@widgy.register
class TableHeader(TableElement):
    draggable = False
    deletable = False
    component_name = 'tableheader'

    class Meta:
        verbose_name = 'columns'

    @classmethod
    def valid_child_of(cls, parent, obj=None):
        if obj in parent.get_children():
            return True
        return (isinstance(parent, Table) and
                len([i for i in parent.get_children() if isinstance(i, cls)]) < 1)

    def valid_parent_of(self, cls, obj=None):
        return issubclass(cls, TableHeaderData)


@widgy.register
class TableBody(InvisibleMixin, TableElement):
    tag_name = 'tbody'

    draggable = False
    deletable = False

    @classmethod
    def valid_child_of(cls, parent, obj=None):
        return isinstance(parent, Table)

    def valid_parent_of(self, cls, obj=None):
        if obj:
            if obj in self.get_children():
                return True
            if isinstance(obj, TableRow) and len(obj.get_children()) == len(self.table.header.get_children()):
                return True
        else:
            return issubclass(cls, TableRow)


@widgy.register
class Table(StrictDefaultChildrenMixin, TableElement):
    tag_name = 'table'
    component_name = 'table'

    shelf = True

    default_children = [
        (TableHeader, (), {}),
        (TableBody, (), {}),
    ]

    @property
    def header(self):
        return self.get_children()[0]

    @property
    def body(self):
        return self.get_children()[1]

    def cells_at_index(self, index):
        return [list(i.get_children())[index] for i in self.body.get_children()]


@widgy.register
class Figure(Content):
    editable = True
    accepting_children = True

    position = models.CharField(default='center', max_length=50, choices=[
        ('left', 'Float left'),
        ('right', 'Float right'),
        ('center', 'Center'),
    ])

    title = models.CharField(blank=True, null=True, max_length=1023)
    caption = models.TextField(blank=True, null=True)


@widgy.register
class Video(Content):
    video = VideoField()

    editable = True
