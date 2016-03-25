from django import forms
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _, ugettext
from django.utils.encoding import python_2_unicode_compatible
from django.dispatch import receiver
from django.template.defaultfilters import truncatechars
from django.contrib.sites.models import Site

from filer.fields.image import FilerImageField

from widgy.models import Content
from widgy.models.mixins import (
    StrictDefaultChildrenMixin, InvisibleMixin, StrDisplayNameMixin,
    TabbedContainer, DefaultChildrenMixin,
)
from widgy.models.links import LinkField, LinkFormField, LinkFormMixin
from widgy.db.fields import WidgyField
from widgy.contrib.page_builder.db.fields import MarkdownField, VideoField, ImageField
from widgy.contrib.page_builder.forms import CKEditorField
from widgy.signals import pre_delete_widget
from widgy.utils import build_url, SelectRelatedManager
import widgy


class BaseLayout(StrictDefaultChildrenMixin, Content):
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


class Layout(BaseLayout):
    """
    Subclasses of Layout will be used to populate WidgyPage root_choices.
    """
    class Meta:
        abstract = True


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
        return isinstance(parent, BaseLayout)

    class Meta:
        verbose_name = _('main content')
        verbose_name_plural = _('main contents')


@widgy.register
class Sidebar(Bucket):
    pop_out = 1

    def valid_parent_of(self, cls, obj=None):
        return not issubclass(cls, (MainContent, Sidebar))

    @classmethod
    def valid_child_of(cls, parent, obj=None):
        return isinstance(parent, BaseLayout)

    class Meta:
        verbose_name = _('sidebar')
        verbose_name_plural = _('sidebars')


@widgy.register
class DefaultLayout(Layout):
    """
    On creation, creates a left and right bucket.
    """
    class Meta:
        verbose_name = _('default layout')
        verbose_name_plural = _('default layouts')

    default_children = [
        ('main', MainContent, (), {}),
        ('sidebar', Sidebar, (), {}),
    ]


@widgy.register
class Markdown(Content):
    content = MarkdownField(blank=True, verbose_name=_('content'))
    rendered = models.TextField(editable=False)

    editable = True
    component_name = 'markdown'

    class Meta:
        verbose_name = _('markdown')
        verbose_name_plural = _('markdowns')


class HtmlForm(forms.ModelForm):
    content = CKEditorField(label=_('Content'))


@widgy.register
class Html(Content):
    content = models.TextField(null=False, default='')

    form = HtmlForm
    editable = True
    tooltip = _("Easily add text to your page with this widget. You can have"
                " certain styles like bold or italic, but they won't break your"
                " design.")

    class Meta:
        verbose_name = _('HTML')
        verbose_name_plural = _('HTML editors')


@widgy.register
class UnsafeHtml(Content):
    content = models.TextField(null=False, default='')

    editable = True
    tooltip = _("If you need to add some JavaScript or an embed code, you can"
                " use this. Staff users should not have access to this"
                " widget.")

    class Meta:
        verbose_name = _('unsafe HTML')
        verbose_name_plural = _('unsafe HTML editors')


@widgy.register
class CalloutBucket(Bucket):
    @classmethod
    def valid_child_of(cls, parent, obj=None):
        return False

    def valid_parent_of(self, cls, obj=None):
        return issubclass(cls, (Markdown, Button, Html))

    class Meta:
        verbose_name = _('callout bucket')
        verbose_name_plural = _('callout buckets')


@python_2_unicode_compatible
class Callout(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('name'))
    site = models.ForeignKey(Site, null=True, blank=True)
    root_node = WidgyField(
        site=settings.WIDGY_MEZZANINE_SITE,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_('Widgy Content'),
        root_choices=(
            'CalloutBucket',
        ))

    class Meta:
        verbose_name = _('callout')
        verbose_name_plural = _('callouts')

    def __str__(self):
        return self.name


@widgy.register
@python_2_unicode_compatible
class CalloutWidget(StrDisplayNameMixin, Content):
    callout = models.ForeignKey(Callout, null=True, blank=True,
                                on_delete=models.PROTECT)

    editable = True
    tooltip = _("Callouts are a way to call a user's attention to something."
                " Callouts can be shared across pages.")

    objects = SelectRelatedManager(select_related=['callout__root_node'])

    class Meta:
        verbose_name = _('callout widget')
        verbose_name_plural = _('callout widgets')

    def __str__(self):
        if self.callout:
            return self.callout.name
        return ''

    @classmethod
    def valid_child_of(cls, parent, obj=None):
        return isinstance(parent, Sidebar)


@widgy.register
class Accordion(DefaultChildrenMixin, Bucket):
    draggable = True
    deletable = True
    tooltip = _("Accordions are a good way to separate sections of content. A"
                " good use for accordions is an FAQ page. Use the Section"
                " widget to separate each section of content in the Accordion.")

    def valid_parent_of(self, cls, obj=None):
        return issubclass(cls, Section)

    class Meta:
        verbose_name = _('accordion')
        verbose_name_plural = _('accordions')

    @property
    def default_children(self):
        """
        Adds 2 Sections as children because you would only ever use an
        Accordion if you had 2 or more Sections.  This increases usability as
        users now don't have to figure out what child Accordion accepts, they
        can follow an example now.  Also, add default titles to the Sections to
        let the user know that Sections need titles.
        """
        return [
            (Section, (), {'title': _('Title 1')}),
            (Section, (), {'title': _('Title 2')}),
        ]


@widgy.register
class Tabs(TabbedContainer, Accordion):
    tooltip = _("Tabs are another way to separate sections of content, but they"
                " are separated horizontally instead of vertically. A good use"
                " for the Tabs widget is a product detail page.")

    class Meta:
        proxy = True
        verbose_name = _('tabs')
        verbose_name_plural = _('tabs')


@widgy.register
@python_2_unicode_compatible
class Section(StrDisplayNameMixin, Content):
    title = models.CharField(max_length=1023, verbose_name=_('title'),
                             help_text=_("Use a unique title for each section."))

    editable = True
    accepting_children = True
    tooltip = _("Use Section to split up your content into more consumable"
                " chunks.")

    @classmethod
    def valid_child_of(cls, parent, obj=None):
        return isinstance(parent, Accordion)

    class Meta:
        verbose_name = _('section')
        verbose_name_plural = _('sections')

    def __str__(self):
        return self.title


@widgy.register
class Image(Content):
    editable = True

    image = FilerImageField(verbose_name=_('image'), null=True,
                            related_name='+', on_delete=models.PROTECT)

    objects = SelectRelatedManager(select_related=['image'])

    class Meta:
        verbose_name = _('image')
        verbose_name_plural = _('images')


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

    tooltip = _("Add a row to your table.")

    @classmethod
    def valid_child_of(cls, parent, obj=None):
        return isinstance(parent, TableBody)

    def valid_parent_of(self, cls, obj=None):
        return issubclass(cls, TableData)

    def post_create(self, site):
        for column in self.table.header.get_children():
            self.add_child(site, TableData)

    class Meta:
        verbose_name = _('row')
        verbose_name_plural = _('rows')


@widgy.register
class TableHeaderData(TableElement):
    tag_name = 'th'

    accepting_children = True
    draggable = True
    deletable = True
    tooltip = _("Add a column to your table.")

    class Meta:
        verbose_name = 'column'

    @classmethod
    def valid_child_of(cls, parent, obj=None):
        if obj and obj.get_parent():
            # we can't be moved to another table
            return obj in parent.get_children()
        else:
            return isinstance(parent, TableHeader)

    def delete_column(self):
        for i in self.table.cells_at_index(self.sibling_index):
            i.node.delete()

    def post_create(self, site):
        right = self.get_next_sibling()
        if right:
            for d in self.table.cells_at_index(right.sibling_index - 1):
                d.add_sibling(site, TableData)
        else:
            for row in self.table.body.get_children():
                row.add_child(site, TableData)

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

    class Meta:
        verbose_name = _('column')
        verbose_name_plural = _('columns')


@receiver(pre_delete_widget, sender=TableHeaderData)
def delete_column(sender, instance, raw, **kwargs):
    if not raw:
        instance.delete_column()


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

    class Meta:
        verbose_name = _('cell')
        verbose_name_plural = _('cells')


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

    class Meta:
        verbose_name = _('table header')
        verbose_name_plural = _('table headers')


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

    class Meta:
        verbose_name = _('table body')
        verbose_name_plural = _('table bodies')


@widgy.register
class Table(StrictDefaultChildrenMixin, TableElement):
    tag_name = 'table'
    component_name = 'table'

    shelf = True
    tooltip = _("With this widget, you can add tables to your page. A good use"
                " for tables is numerical data or comparing things side by"
                " side.")

    default_children = [
        ('header', TableHeader, (), {}),
        ('body', TableBody, (), {}),
    ]

    @property
    def header(self):
        return self.children['header']

    @property
    def body(self):
        return self.children['body']

    def cells_at_index(self, index):
        return [list(i.get_children())[index] for i in self.body.get_children()]

    class Meta:
        verbose_name = _('table')
        verbose_name_plural = _('tables')


@widgy.register
@python_2_unicode_compatible
class Figure(StrDisplayNameMixin, Content):
    editable = True
    accepting_children = True
    tooltip = _("A figure is a self-contained piece of content. It can be used"
                " to add a caption to an image or a video for example.")

    position = models.CharField(default=_('center'), verbose_name=_('position'), max_length=50, choices=[
        ('left', _('Float left')),
        ('right', _('Float right')),
        ('center', _('Center')),
    ])

    title = models.CharField(blank=True, null=True, max_length=1023, verbose_name=_('title'))
    caption = models.TextField(blank=True, null=True, verbose_name=_('caption'))

    class Meta:
        verbose_name = _('figure')
        verbose_name_plural = _('figures')

    def __str__(self):
        return self.title or ''


@widgy.register
@python_2_unicode_compatible
class Video(StrDisplayNameMixin, Content):
    video = VideoField(verbose_name=_('video'))

    editable = True
    tooltip = _("Add a video to your page. Supports YouTube, Vimeo, and"
                " others.")

    class Meta:
        verbose_name = _('video')
        verbose_name_plural = _('videos')

    def __str__(self):
        return self.video


class ButtonForm(LinkFormMixin, forms.ModelForm):
    link = LinkFormField(label=_('Link'), required=False)


@widgy.register
@python_2_unicode_compatible
class Button(StrDisplayNameMixin, Content):
    text = models.CharField(max_length=255, verbose_name=_('text'), null=True, blank=True)

    link = LinkField(null=True)

    css_classes = ('page_builder', 'buttonwidget')
    form = ButtonForm
    editable = True
    tooltip = _("Add a link to another page.")

    objects = SelectRelatedManager(prefetch_related=['link'])

    class Meta:
        verbose_name = _('button')
        verbose_name_plural = _('buttons')

    def __str__(self):
        if self.text is not None:
            return self.text
        return ''


@widgy.register
@python_2_unicode_compatible
class GoogleMap(StrDisplayNameMixin, Content):
    MAP_CHOICES = (
        ('roadmap', _('Road map')),
        ('satellite', _('Satellite')),
        ('hybrid', _('Hybrid')),
        ('terrain', _('Terrain')),
    )

    address = models.CharField(_('address'), max_length=500)
    type = models.CharField(_('type'), max_length=20,
                            choices=MAP_CHOICES,
                            default=MAP_CHOICES[0][0])

    editable = True
    tooltip = _("This will output a map on your page with an address that you"
                " specify.")

    zoom = 15

    class Meta:
        verbose_name = _('Google map')
        verbose_name_plural = _('Google maps')

    def __str__(self):
        return truncatechars(self.address, 35)

    def get_maptype_short(self):
        return {
            'roadmap': 'm',
            'satellite': 'k',
            'hybrid': 'h',
            'terrain': 'p',
        }.get(self.type, 'm')

    def get_map_options(self):
        from django.utils.translation import get_language
        return {
            'q': self.address,
            'hl': get_language(),
            'ie': 'UTF8',
            'iwloc': 'addr',
            't': self.get_maptype_short(),
            'vector': 1,
            'z': self.zoom,
        }

    def get_embed_url(self):
        options = self.get_map_options()
        options['output'] = 'embed'
        return build_url('https://maps.google.com/', **options)

    def get_absolute_url(self):
        options = self.get_map_options()
        options['source'] = 'embed'
        return build_url('https://maps.google.com/', **options)

    def get_preview_url(self):
        options = {
            'size': '300x200',
            'zoom': self.zoom,
            'maptype': self.type,
            'sensor': 'true',
            'markers': '|%s' % self.address,
        }
        return build_url('https://maps.googleapis.com/maps/api/staticmap', **options)
