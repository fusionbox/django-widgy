from django.contrib import admin
from django.template.response import TemplateResponse

from mezzanine.pages.admin import PageAdmin

from .models import ContentPage


class ContentPageAdmin(PageAdmin):
    model = ContentPage

    def add_view(self, request, extra_context=None):
        pass

    def change_view(self, request, object_id, extra_context=None):
        template = 'admin/widgy/change_form.html'
        env = {}

        if request.method == 'POST':
            pass
        else:
            res = super(ContentPageAdmin, self).change_view(request, object_id, extra_context)
            env.update(res.context_data)

        return TemplateResponse(request, template, env)

    def delete_view(self, request, object_id, extra_context=None):
        pass


admin.site.register(ContentPage, ContentPageAdmin)
