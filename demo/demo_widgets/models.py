from django.db import models
from django.utils.translation import ugettext_lazy as _

import widgy
from widgy.models import Content
from widgy.models.mixins import StrDisplayNameMixin
from widgy.contrib.page_builder.models import (
    DefaultLayout, ImageField, Html, Button
)


class AcceptsSimpleHtmlChildrenMixin(object):
    def valid_parent_of(self, cls, obj=None):
        return issubclass(cls, (Html, Button))


@widgy.register
class Slide(StrDisplayNameMixin, AcceptsSimpleHtmlChildrenMixin, Content):
    tagline = models.CharField(_('tagline'), max_length=255)
    background_image = ImageField(verbose_name=_('background image'))

    editable = True

    def __unicode__(self):
        return self.tagline

    @classmethod
    def valid_child_of(cls, parent, obj=None):
        return isinstance(parent, Slideshow)


@widgy.register
class Slideshow(Content):
    @classmethod
    def valid_child_of(cls, parent, obj):
        return isinstance(parent, HomeLayout)

    def valid_parent_of(self, cls, obj=None):
        return issubclass(cls, Slide)


@widgy.register
class Box(StrDisplayNameMixin, AcceptsSimpleHtmlChildrenMixin, Content):
    title = models.CharField(verbose_name=_('title'), max_length=255)

    editable = True

    def __unicode__(self):
        return self.title

    @classmethod
    def valid_child_of(cls, parent, obj=None):
        return isinstance(parent, Boxes)


@widgy.register
class Boxes(Content):
    @classmethod
    def valid_child_of(cls, parent, obj):
        return isinstance(parent, HomeLayout)

    def valid_parent_of(self, cls, obj=None):
        # Accept up to 3 Box chilren
        return (obj in self.get_children() or
                (issubclass(cls, Box) and len(self.get_children()) < 3))


@widgy.register
class HomeLayout(DefaultLayout):
    default_children = (
        ('slideshow', Slideshow, (), {}),
        ('boxes', Boxes, (), {}),
    )

    class Meta:
        proxy = True
        verbose_name = _('home layout')
        verbose_name_plural = _('home layouts')
