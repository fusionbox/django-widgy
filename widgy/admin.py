from django.contrib import admin

from mezzanine.pages.admin import PageAdmin

from widgy.models import ContentPage


class WidgyPageAdmin(PageAdmin):
    """
    Model Admin for models which will have a widgy tree under them
    """
    pass


admin.site.register(ContentPage, WidgyPageAdmin)

# Remove built in Django and Mezzanine models from the admin center
from django.contrib.auth.models import Group
from mezzanine.generic.models import ThreadedComment
from mezzanine.pages.models import RichTextPage

admin.site.unregister(RichTextPage)
admin.site.unregister(ThreadedComment)
admin.site.unregister(Group)
