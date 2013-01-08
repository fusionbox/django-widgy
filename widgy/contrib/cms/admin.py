if False:
    from django.contrib import admin
    from widgy.admin import WidgyAdmin

    from mezzanine.pages.admin import PageAdmin

    from widgy.contrib.cms.models import ContentPage, Callout


    class WidgyPageAdmin(PageAdmin, WidgyAdmin):
        pass


    admin.site.register(ContentPage, WidgyPageAdmin)
    admin.site.register(Callout)

    # Remove built in Django and Mezzanine models from the admin center
    from django.contrib.auth.models import Group
    from mezzanine.pages.models import RichTextPage

    admin.site.unregister(RichTextPage)
    admin.site.unregister(Group)
