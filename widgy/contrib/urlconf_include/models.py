from django.db import models
from django.utils.translation import ugettext_lazy as _

from mezzanine.pages.models import Page

class UrlconfIncludePage(Page):
    urlconf_name = models.CharField(max_length=255, verbose_name=_('urlconf name'))

    def can_add(self, request):
        return False

    def overridden(self):
        # this normally returns True if the page has a urlconf pointing to it,
        # to disallow slug editing. Our urlconf always points to whatever our
        # slug is, so it's ok to edit.
        return False

    class Meta:
        verbose_name = _('urlconf include page')
        verbose_name_plural = _('urlconf include pages')
