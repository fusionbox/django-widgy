from django.contrib import admin
from django.conf import settings

from widgy.admin import WidgyAdmin
from mezzanine.pages.admin import PageAdmin
from widgy.contrib.widgy_mezzanine.models import WidgyPage
from widgy.utils import fancy_import


class WidgyPageAdmin(PageAdmin, WidgyAdmin):
    change_form_template = 'widgy/page_builder/widgypage_change_form.html'

    def get_site(self):
        return fancy_import(settings.WIDGY_MEZZANINE_SITE)

    def render_change_form(self, request, context, *args, **kwargs):
        if 'original' in context and context['original'].root_node:
            # we are rendering a change form
            obj = context['original']
            site = self.get_site()
            context['history_url'] = site.reverse(site.history_view, kwargs={'pk': obj.root_node.pk})
        return super(WidgyPageAdmin, self).render_change_form(request, context, *args, **kwargs)


# Remove built in Mezzanine models from the admin center
from mezzanine.pages.models import RichTextPage

admin.site.unregister(RichTextPage)

admin.site.register(WidgyPage, WidgyPageAdmin)
