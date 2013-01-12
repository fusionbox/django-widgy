from django.db import models

from widgy.models import Content
from widgy.db.fields import WidgyField
from widgy import registry

from .widgy_config import widgy_site


class Layout(Content):
    @classmethod
    def valid_child_of(self, parent, obj=None):
        return False

    def valid_parent_of(self, cls, obj=None):
        return issubclass(cls, Bucket)

    def post_create(self, site):
        self.add_child(site, Bucket)
        self.add_child(site, Bucket)


class Bucket(Content):
    pass


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

registry.register(Layout)
registry.register(Bucket)
registry.register(RawTextWidget)
registry.register(CantGoAnywhereWidget)
registry.register(PickyBucket)
registry.register(ImmovableBucket)
registry.register(AnotherLayout)


class HasAWidgy(models.Model):
    widgy = WidgyField(
        root_choices=[Layout],
        site=widgy_site
    )


class HasAWidgyOnlyAnotherLayout(models.Model):
    widgy = WidgyField(
        root_choices=[AnotherLayout],
        site=widgy_site
    )


class UnregisteredLayout(Layout):
    pass
