from django.contrib import admin

from widgy.admin import WidgyAdmin
from widgy.contrib.page_builder.models import Callout


class CalloutAdmin(WidgyAdmin):
    fields = ('name', 'root_node', )

admin.site.register(Callout, CalloutAdmin)
