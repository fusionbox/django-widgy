from __future__ import absolute_import

from django.contrib import admin

from widgy.site import WidgySite
from widgy.contrib.widgy_mezzanine.models import WidgyPage
from widgy.contrib.widgy_mezzanine.admin import WidgyPageAdmin


widgy_site = WidgySite()


class WidgyPageAdmin(WidgyPageAdmin):
    site = widgy_site


admin.site.register(WidgyPage, WidgyPageAdmin)
