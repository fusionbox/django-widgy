from django.db import models

from widgy.models import Content


class Layout(Content):
    accepting_children = True

    @classmethod
    def valid_child_class_of(self, cls):
        return False

    def valid_parent_of_class(self, cls):
        return issubclass(cls, Bucket)

    def post_create(self):
        self.add_child(Bucket)
        self.add_child(Bucket)


class Bucket(Content):
    accepting_children = True


class RawTextWidget(Content):
    text = models.TextField()

    def __unicode__(self):
        return self.text


class CantGoAnywhereWidget(Content):
    @classmethod
    def valid_child_class_of(self, content):
        return False

    def valid_parent_of_class(self, cls):
        return False


class PickyBucket(Bucket):
    def valid_parent_of_class(self, cls):
        return issubclass(cls, RawTextWidget)

    def valid_parent_of_instance(self, content):
        return (self.valid_parent_of_class(type(content)) and
                content.text == 'hello')


class ImmovableBucket(Bucket):
    draggable = False
