from django.db import models

from widgy.models import Content
from widgy.db.fields import WidgyField, VersionedWidgyField
from widgy import registry

from widgy.models.links import LinkableMixin, LinkField
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


class RawTextWidget(Content):
    text = models.TextField()

    def __unicode__(self):
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


class WeirdPkBase(Content):
    bubble = models.AutoField(primary_key=True)


class WeirdPkBucketBase(WeirdPkBase):
    pass


class WeirdPkBucket(WeirdPkBucketBase):
    pass


class ImmovableBucket(Bucket):
    draggable = False


class AnotherLayout(Layout):
    pass


class VowelBucket(Bucket):
    class Meta:
        proxy = True

    def valid_parent_of(self, cls, obj=None):
        return cls.__name__[0].lower() in 'aeiou'


class UndeletableRawTextWidget(RawTextWidget):
    deletable = False

    class Meta:
        proxy = True

registry.register(Layout)
registry.register(Bucket)
registry.register(RawTextWidget)
registry.register(CantGoAnywhereWidget)
registry.register(PickyBucket)
registry.register(ImmovableBucket)
registry.register(AnotherLayout)
registry.register(VowelBucket)


class HasAWidgy(models.Model):
    widgy = WidgyField(
        root_choices=[Layout],
        site='modeltests.core_tests.widgy_config.widgy_site',
    )


class HasAWidgyOnlyAnotherLayout(models.Model):
    widgy = WidgyField(
        root_choices=[AnotherLayout],
        site='modeltests.core_tests.widgy_config.widgy_site'
    )


class UnregisteredLayout(Layout):
    pass


class VersionedPage(models.Model):
    version_tracker = VersionedWidgyField(
        site='modeltests.core_tests.widgy_config.widgy_site',
        root_choices=[Layout, AnotherLayout],
    )


class VersionedPage2(models.Model):
    bar = VersionedWidgyField(site='modeltests.core_tests.widgy_config.widgy_site', related_name='asdf')


class VersionedPage3(models.Model):
    foo = VersionedWidgyField(site='modeltests.core_tests.widgy_config.widgy_site', related_name='+')


class VersionedPage4(models.Model):
    widgies = models.ManyToManyField('widgy.VersionTracker', through='VersionPageThrough')


class VersionPageThrough(models.Model):
    widgy = VersionedWidgyField(site='modeltests.core_tests.widgy_config.widgy_site', related_name='+')
    page = models.ForeignKey(VersionedPage4)


class Related(models.Model):
    pass


class ForeignKeyWidget(Content):
    foo = models.ForeignKey(Related, on_delete=models.CASCADE)

registry.register(ForeignKeyWidget)


class LinkableThing(LinkableMixin, models.Model):
    name = models.CharField(max_length=255, default='')

    def __unicode__(self):
        return self.name


class AnotherLinkableThing(LinkableMixin, models.Model):
    pass


class ThingWithLink(models.Model):
    link = LinkField('linkable_content_type', 'linkable_object_id')


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
