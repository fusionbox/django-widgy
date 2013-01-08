from django.contrib import admin

from widgy.admin import WidgyAdmin
from widgy.contrib.page_builder.models import Callout

admin.site.register(Callout, WidgyAdmin)
