from django.db import models
from django.utils.translation import (
    ugettext_lazy as _, ugettext, get_language, get_language_info
)
from django.conf import settings

from widgy.models import Content
from widgy.contrib.page_builder.models import Layout
from widgy.models.mixins import TabbedContainer, StrictDefaultChildrenMixin
from widgy import register


class I18NChild(models.Model):
    """
    Mixin for Contents that go directly inside I18NTabbedContainers.
    """
    language_code = models.CharField(verbose_name=_('Layout'),
                                     max_length=2,
                                     choices=settings.LANGUAGES,
                                     )

    class Meta:
        abstract = True

    @property
    def language_name(self):
        info = get_language_info(self.language_code)
        return ugettext(info['name'])

    @property
    def display_name(self):
        return self.language_name


class I18NTabbedContainer(TabbedContainer, Content):
    """
    A TabbedContainer that chooses which child to render based on the
    current language.  You should only put I18NChild in this as children.
    """
    class Meta:
        abstract = True

    def render(self, *args, **kwargs):
        current_language = get_language()
        try:
            child = self.get_child_for_language(current_language)
        except IndexError:
            child = self.get_child_for_language(current_language[0:2])
        return child.render(*args, **kwargs)

    def get_child_for_language(self, code):
        return [child for child in self.get_children() if child.language_code == code][0]


@register
class I18NLayout(I18NChild, Layout):
    """
    This is a layout for a specific language that lives inside a
    I18NLayoutContainer.
    """
    @classmethod
    def valid_child_of(cls, content, obj=None):
        return isinstance(content, I18NLayoutContainer)


@register
class I18NLayoutContainer(StrictDefaultChildrenMixin, I18NTabbedContainer):
    """
    A root node that holds different language versions of the same page.
    """
    child_class = I18NLayout
    draggable = False
    editable = False
    deletable = False

    @property
    def default_children(self):
        return [
            (l[0], self.child_class, (), {'language_code': l[0]})
            for l in settings.LANGUAGES
        ]

    @classmethod
    def valid_child_of(self, content, obj=None):
        return False
