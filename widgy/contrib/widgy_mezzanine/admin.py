from django.contrib import admin
from widgy.admin import WidgyAdmin

from mezzanine.pages.admin import PageAdmin
from widgy.contrib.widgy_mezzanine.models import WidgyPage


class WidgyPageAdmin(PageAdmin, WidgyAdmin):
    pass


# Remove built in Mezzanine models from the admin center
from mezzanine.pages.models import RichTextPage

admin.site.unregister(RichTextPage)

admin.site.register(WidgyPage, WidgyPageAdmin)
