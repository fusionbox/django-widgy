from django.contrib import admin

from mezzanine.pages.admin import PageAdmin

from widgy.contrib.cms.models import ContentPage, Callout, CalloutContent
from widgy.forms import WidgyFormMixin


class WidgyPageAdmin(PageAdmin):
    """
    Model Admin for models which will have a widgy tree under them
    """
    def get_form(self, request, obj=None, **kwargs):
        form = super(WidgyPageAdmin, self).get_form(request, obj, **kwargs)

        if not issubclass(form, WidgyFormMixin):
            class form(WidgyFormMixin, form):
                pass

        return form


admin.site.register(ContentPage, WidgyPageAdmin)
admin.site.register(Callout)
admin.site.register(CalloutContent)

# Remove built in Django and Mezzanine models from the admin center
from django.contrib.auth.models import Group
from mezzanine.generic.models import ThreadedComment
from mezzanine.pages.models import RichTextPage

admin.site.unregister(RichTextPage)
admin.site.unregister(ThreadedComment)
admin.site.unregister(Group)
