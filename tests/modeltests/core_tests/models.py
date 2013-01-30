from django.db import models

from widgy.models import Content
from widgy.db.fields import WidgyField, VersionedWidgyField
from widgy import registry

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


class Bucket(Content):
    accepting_children = True


class RawTextWidget(Content):
    text = models.TextField()

    def __unicode__(self):
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


class ImmovableBucket(Bucket):
    draggable = False


class AnotherLayout(Layout):
    pass


class VowelBucket(Bucket):
    class Meta:
        proxy = True

    def valid_parent_of(self, cls, obj=None):
        return cls.__name__[0].lower() in 'aeiou'

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
    version_tracker = VersionedWidgyField(site='modeltests.core_tests.widgy_config.widgy_site')


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
