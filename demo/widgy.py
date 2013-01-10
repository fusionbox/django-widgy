from __future__ import absolute_import

from django.contrib import admin

from widgy.site import WidgySite
from widgy.admin import WidgyAdmin
from widgy.contrib.widgy_mezzanine.models import WidgyPage
from widgy.contrib.widgy_mezzanine.admin import WidgyPageAdmin
from widgy.contrib.page_builder.models import Callout

widgy_site = WidgySite()


class WidgyAdmin(WidgyAdmin):
    site = widgy_site


class WidgyPageAdmin(WidgyPageAdmin):
    site = widgy_site


admin.site.register(WidgyPage, WidgyPageAdmin)

admin.site.register(Callout, WidgyAdmin)
