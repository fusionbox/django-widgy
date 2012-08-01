from django.contrib import admin
from django.template.response import TemplateResponse
from django.shortcuts import get_object_or_404
from django.conf.urls import patterns, url

from mezzanine.pages.admin import PageAdmin

from widgy.models import ContentPage, Node

from django import forms


class WidgyPageAdmin(PageAdmin):
    model = ContentPage

    add_form_template = 'admin/widgy/change_form.html'
    change_form_template = 'admin/widgy/change_form.html'

    def get_form(self, *args, **kwargs):
        form = super(WidgyPageAdmin, self).get_form(*args, **kwargs)
        return form

    def 
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if issubclass(db_field.rel.to, Node)
            layouts = self.model.get_valid_layouts()
            ContentType.objects.filter(
            kwargs["queryset"] = 
        return super(WidgyPageAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    ##|
    ##| Views
    ##|
    def get_urls(self):
        urls = super(WidgyPageAdmin, self).get_urls()
        my_urls = patterns('',
            url(r'^(?P<page_pk>[0-9]+)/edit-widget/(?P<node_pk>[0-9]+)/$', self.admin_site.admin_view(self.edit_widget), name='edit_widget'),
        )
        return my_urls + urls

    def add_view(self, request, extra_context={}):
        extra_context['layout_form'] = LayoutSelectForm(self.model)
        res = super(WidgyPageAdmin, self).add_view(request, extra_context)

        return res

    def change_view(self, request, object_id, extra_context=None):
        pass

    def edit_widget(self, request, page_pk, node_pk):
        template = 'admin/widgy/widgy_edit.html'
        env = {}

        res = super(WidgyPageAdmin, self).change_view(request, page_pk, None)
        env.update(res.context_data)

        page = get_object_or_404(ContentPage, pk=page_pk)
        env['page'] = page

        return TemplateResponse(request, 'admin/widgy/widgy_edit.html', env)

        return TemplateResponse(request, template, env)

admin.site.register(ContentPage, WidgyPageAdmin)
