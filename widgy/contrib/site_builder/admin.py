from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponseRedirectBase
from django.shortcuts import redirect

from widgy.admin import WidgyAdmin

from widgy.contrib.site_builder.models import WidgySite, ContentPage, InternalRedirect, ExternalRedirect
from widgy.contrib.site_builder.forms import ContentPageForm


class PageAdmin(WidgyAdmin):
    def change_view(self, request, object_id, *args, **kwargs):
        response = super(PageAdmin, self).change_view(request, object_id, *args, **kwargs)
        if isinstance(response, HttpResponseRedirectBase):
            root_node = self.queryset(request).get(pk=object_id).get_root().node
            site_root = WidgySite.objects.get(root_node=root_node)
            return redirect(site_root.get_edit_url())
        return response


class WidgySiteAdmin(WidgyAdmin):
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ('site',)
        return super(WidgySiteAdmin, self).get_readonly_fields(request, obj)

admin.site.register(WidgySite, WidgySiteAdmin)
admin.site.register(InternalRedirect, PageAdmin)
admin.site.register(ExternalRedirect, PageAdmin)


class ContentPageAdmin(PageAdmin):
    form = ContentPageForm
    exclude = ('slug',)
    fieldsets = (
        (None, {'fields': ('title',)}),
        (_('Page Meta'), {'fields': (('publish_at', 'is_published'), 'is_included_in_sitemap')}),
        (_('SEO Fields'), {
            'fields': ('seo_title', 'seo_description', 'seo_keywords'),
            'classes': ('colapse',),
        }),
        (_('Page Content'), {'fields': ('root_node',)}),
    )
    fieldsets = None

    def has_add_permission(self, request):
        return False

admin.site.register(ContentPage, PageAdmin)
