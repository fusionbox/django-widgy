from django.db import models
from django.core import urlresolvers

from mezzanine.pages.page_processors import processor_for
from mezzanine.pages.models import Page

class UrlconfIncludePage(Page):
    urlconf_name = models.CharField(max_length=255)

    def can_add(self, request):
        # This won't actually do anything until
        # https://github.com/stephenmcd/mezzanine/issues/349 is fixed
        return False
