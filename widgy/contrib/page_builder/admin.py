from django.contrib import admin
from django.contrib.sites.models import Site

from widgy.admin import WidgyAdmin
from widgy.contrib.page_builder.models import Callout


class CalloutAdmin(WidgyAdmin):
    def get_fields(self, request, obj=None):
        # Mezzanine has a weird data model for site permissions. This optimizes the query into
        # one single SQL statement. This also avoids raising an ObjectDoesNotExist error in case
        # a user does not have a sitepermission object.
        site_list = Site.objects.filter(sitepermission__user=request.user)

        if request.user.is_superuser or len(site_list) > 1:
            return ('name', 'site', 'root_node')
        else:
            return ('name', 'root_node')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'site' and not request.user.is_superuser:
            # See CalloutAdmin.get_fields() about this query
            kwargs['queryset'] = Site.objects.filter(sitepermission__user=request.user)

            # Non superusers have to select a site, otherwise the callout will be global.
            kwargs['required'] = True
        return super(CalloutAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        site_list = Site.objects.filter(sitepermission__user=request.user)
        if not change and len(site_list) == 1:
            obj.site = site_list.get()
        return super(CalloutAdmin, self).save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super(CalloutAdmin, self).get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(site__sitepermission__user=request.user)
        return qs


admin.site.register(Callout, CalloutAdmin)
