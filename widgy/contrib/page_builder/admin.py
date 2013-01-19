from django.contrib import admin

from filer.admin.fileadmin import FileAdmin

from widgy.admin import WidgyAdmin
from widgy.contrib.page_builder.models import Callout, WidgyImageFile

admin.site.register(Callout, WidgyAdmin)
admin.site.register(WidgyImageFile, FileAdmin)
