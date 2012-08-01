import operator

from django.contrib import admin
from django.template.response import TemplateResponse
from django.shortcuts import get_object_or_404
from django.conf.urls import patterns, url
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from mezzanine.pages.admin import PageAdmin

from widgy.models import ContentPage, Node, Content

from django import forms


class WidgyPageForm(forms.ModelForm):
    layout_content_type = forms.ModelChoiceField(queryset=ContentType.objects.none())

    class Meta:
        model = ContentPage
        exclude = ('root_node',)


class WidgyPageAdmin(PageAdmin):
    form = WidgyPageForm

    add_form_template = 'admin/widgy/change_form.html'
    change_form_template = 'admin/widgy/change_form.html'

    def get_form(self, *args, **kwargs):
        form = super(WidgyPageAdmin, self).get_form(*args, **kwargs)
        layouts = self.model.get_valid_layouts()
        qs = [Q(app_label=c._meta.app_label, model=c._meta.module_name) for c in layouts]
        form.base_fields['layout_content_type'].queryset = ContentType.objects.filter(
                reduce(operator.or_, qs))
        return form

    def get_fieldsets(self, request, obj=None):
        fieldsets = super(WidgyPageAdmin, self).get_fieldsets(request, obj)
        if not obj and 'layout_content_type' not in fieldsets[0][1]['fields']:
            fieldsets[0][1]['fields'].append('layout_content_type')

        # https://github.com/stephenmcd/mezzanine/pull/354
        try:
            fieldsets[0][1]['fields'].remove('root_node')
        except ValueError:
            pass

        return fieldsets

    def save_model(self, request, obj, form, change):
        if not change:
            obj.root_node = form.cleaned_data['layout_content_type'].model_class().add_root().node
        super(WidgyPageAdmin, self).save_model(request, obj, form, change)

    ##|
    ##| Views
    ##|
    def get_urls(self):
        urls = super(WidgyPageAdmin, self).get_urls()
        my_urls = patterns('',
            url(r'^(?P<page_pk>[0-9]+)/edit-widget/(?P<node_pk>[0-9]+)/$', self.admin_site.admin_view(self.edit_widget), name='edit_widget'),
        )
        return my_urls + urls

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
