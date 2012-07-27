from django.db import models
from django.core import urlresolvers

from mezzanine.pages.page_processors import processor_for
from mezzanine.pages.models import Page

class UrlconfIncludePage(Page):
    urlconf_name = models.CharField(max_length=255)
