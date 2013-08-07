from django.db import models
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from mezzanine.pages.models import Page

from widgy.models import links

URLCONF_INCLUDE_CHOICES = getattr(settings, 'URLCONF_INCLUDE_CHOICES', None)
# Application developers using widgy.contrib.urlconf_include should set
# settings.URLCONF_INCLUDE_CHOICES.
# If URLCONF_INCLUDE_CHOICES is None, this lets the user enter any urlconf_name:
#   * if urlconf_name module doesn't exist, this breaks the whole site
#   * if urlconf_name is a module executing code during the importation,
# this can lead to remote code execution.
if URLCONF_INCLUDE_CHOICES is None:
    raise ImproperlyConfigured('URLCONF_INCLUDE_CHOICES setting should '
                               'be a list of choices of urls modules')


@links.register
class UrlconfIncludePage(Page):
    urlconf_name = models.CharField(max_length=255, verbose_name=_('plugin name'),
                                    choices=URLCONF_INCLUDE_CHOICES)

    def can_add(self, request):
        return False

    def overridden(self):
        # this normally returns True if the page has a urlconf pointing to it,
        # to disallow slug editing. Our urlconf always points to whatever our
        # slug is, so it's ok to edit.
        return False

    class Meta:
        verbose_name = _('plugin')
        verbose_name_plural = _('plugins')
