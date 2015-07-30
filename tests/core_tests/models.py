# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _

from widgy.models import Content
from widgy.db.fields import WidgyField, VersionedWidgyField
from widgy import registry
from django.utils.encoding import python_2_unicode_compatible

from widgy.models import links
from widgy.models.mixins import InvisibleMixin


class Layout(Content):
    accepting_children = True

    @classmethod
    def valid_child_of(self, parent, obj=None):
        return False

    def valid_parent_of(self, cls, obj=None):
        return issubclass(cls, Bucket)

    def post_create(self, site):
        self.add_child(site, Bucket)
        self.add_child(site, Bucket)

    def render(self, context, template=None):
        return ''.join(i.render(context) for i in self.get_children())


class Bucket(Content):
    accepting_children = True

    def render(self, context, template=None):
        return ''.join(i.render(context) for i in self.get_children())

    class Meta:
        # test that stuff works with lazily translated strings
        verbose_name = _("bucket")


@python_2_unicode_compatible
class RawTextWidget(Content):
    text = models.TextField()

    def __str__(self):
        return self.text

    def render(self, context):
        return self.text


class CantGoAnywhereWidget(Content):
    @classmethod
    def valid_child_of(cls, parent, obj=None):
        return False

    def valid_parent_of(self, cls, obj=None):
        return False


class PickyBucket(Bucket):
    def valid_parent_of(self, cls, obj=None):
        if obj:
            return (self.valid_parent_of(cls) and
                    obj.text == 'hello')
        return issubclass(cls, RawTextWidget)


class CssClassesWidget(Content):
    css_classes = ('foo', 'bar')


class CssClassesWidgetSubclass(CssClassesWidget):
    class Meta:
        proxy = True


class CssClassesWidgetProperty(CssClassesWidget):
    @property
    def css_classes(self):
        return ('baz', 'qux')


class WeirdPkBase(Content):
    bubble = models.AutoField(primary_key=True)


class WeirdPkBucketBase(WeirdPkBase):
    pass


class WeirdPkBucket(WeirdPkBucketBase):
    pass


class ImmovableBucket(Bucket):
    draggable = False


class AnotherLayout(Layout):
    class Meta:
        # This tests verbose names that have unicode characters
        verbose_name = 'Àñöthér Làyöùt'
        verbose_name_plural = 'Àñöthér Làyöùts'


class VowelBucket(Bucket):
    class Meta:
        proxy = True

    def valid_parent_of(self, cls, obj=None):
        return cls.__name__[0].lower() in 'aeiou'


class UndeletableRawTextWidget(RawTextWidget):
    deletable = False

    class Meta:
        proxy = True

class UnnestableWidget(Bucket):
    @classmethod
    def valid_child_of(cls, parent, obj=None):
        for p in list(parent.get_ancestors()) + [parent]:
            if isinstance(p, UnnestableWidget):
                return False
        return super(UnnestableWidget, cls).valid_child_of(parent, obj)

registry.register(Layout)
registry.register(Bucket)
registry.register(RawTextWidget)
registry.register(CantGoAnywhereWidget)
registry.register(PickyBucket)
registry.register(ImmovableBucket)
registry.register(AnotherLayout)
registry.register(VowelBucket)
registry.register(UnnestableWidget)


class HasAWidgy(models.Model):
    widgy = WidgyField(
        null=True,
        blank=True,
        root_choices=[Layout],
        site='tests.core_tests.widgy_config.widgy_site',
    )

class HasAWidgyNonNull(models.Model):
    widgy = WidgyField(
        root_choices=[AnotherLayout],
        site='tests.core_tests.widgy_config.widgy_site',
    )


class HasAWidgyOnlyAnotherLayout(models.Model):
    widgy = WidgyField(
        null=True,
        blank=True,
        root_choices=[AnotherLayout],
        site='tests.core_tests.widgy_config.widgy_site'
    )


class UnregisteredLayout(Layout):
    pass


class VersionedPage(models.Model):
    version_tracker = VersionedWidgyField(
        site='tests.core_tests.widgy_config.widgy_site',
        root_choices=[Layout, AnotherLayout],
        blank=True,
        null=True,
    )


class VersionedPage2(models.Model):
    bar = VersionedWidgyField(
        site='tests.core_tests.widgy_config.widgy_site',
        related_name='asdf',
        null=True
    )


class VersionedPage3(models.Model):
    foo = VersionedWidgyField(
        site='tests.core_tests.widgy_config.widgy_site', related_name='+')


class VersionedPage4(models.Model):
    widgies = models.ManyToManyField('widgy.VersionTracker', through='VersionPageThrough')


class VersionPageThrough(models.Model):
    widgy = VersionedWidgyField(
        site='tests.core_tests.widgy_config.widgy_site', related_name='+')
    page = models.ForeignKey(VersionedPage4)


class Related(models.Model):
    pass


class ForeignKeyWidget(Content):
    foo = models.ForeignKey(Related, on_delete=models.CASCADE)

registry.register(ForeignKeyWidget)


@links.register
@python_2_unicode_compatible
class LinkableThing(models.Model):
    name = models.CharField(max_length=255, default='')

    def __str__(self):
        return self.name


@links.register
class AnotherLinkableThing(models.Model):
    pass


@links.register
class LinkableThing3(models.Model):
    class Meta:
        verbose_name_plural = _('ZZZZZ should be last')


class ThingWithLink(models.Model):
    link = links.LinkField('linkable_content_type', 'linkable_object_id')


class ChildThingWithLink(ThingWithLink):
    pass


class MyInvisibleBucket(InvisibleMixin, Content):
    """
    This is for testing template hierarchy
    """
    pass


class VariegatedFieldsWidget(Content):
    required_name = models.CharField(max_length=255)
    optional_name = models.CharField(max_length=255, blank=True)
    color = models.CharField(max_length=255, choices=(
        ('r', 'Red'),
        ('g', 'Green'),
        ('b', 'Blue'),
    ))
    date = models.DateField(null=True)
    time = models.TimeField(null=True)
    datetime = models.DateTimeField(null=True)


class ReviewedVersionedPage(models.Model):
    version_tracker = VersionedWidgyField(
        site='tests.core_tests.widgy_config.widgy_site',
        root_choices=[Layout, AnotherLayout],
        to='review_queue.ReviewedVersionTracker',
    )


# This just tests that it is possible to have two widgets of the same name in
# different apps.
class Button(Content):
    pass


class WidgetWithHTMLHelpText(Content):
    name = models.CharField(max_length=255, help_text="Your<br>Name")


class VerboseNameLayout(Content):
    pass


class VerboseNameLayoutChild(VerboseNameLayout):
    class Meta:
        verbose_name = 'Foobar'


class Tag(models.Model):
    name = models.CharField(unique=True, max_length=100)


@registry.register
class ManyToManyWidget(Content):
    tags = models.ManyToManyField(Tag)
