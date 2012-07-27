from django.contrib import admin

from mezzanine.pages.admin import PageAdmin

from .models import UrlconfIncludePage

admin.site.register(UrlconfIncludePage, PageAdmin)
