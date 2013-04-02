from django.contrib import admin

from widgy.admin import WidgyAdmin

from demo.demo_widgets.models import I18NThing


admin.site.register(I18NThing, WidgyAdmin)
