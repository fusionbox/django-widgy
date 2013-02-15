from django.contrib import admin
from django.conf import settings
from django import forms
from django.core.urlresolvers import reverse
from django.contrib.admin.util import quote

from mezzanine.pages.admin import PageAdmin
try:
    from mezzanine.pages.admin import PageAdminForm
except ImportError:
    PageAdminForm = forms.ModelForm

from mezzanine.core.models import (CONTENT_STATUS_PUBLISHED,
                                   CONTENT_STATUS_DRAFT)

from widgy.admin import WidgyAdmin
from widgy.contrib.widgy_mezzanine.models import WidgyPage
from widgy.utils import fancy_import, format_html


class WidgyPageAdminForm(PageAdminForm):
    def __init__(self, *args, **kwargs):
        super(WidgyPageAdminForm, self).__init__(*args, **kwargs)
        self.fields['status'].initial = CONTENT_STATUS_DRAFT

    def clean_status(self):
        status = self.cleaned_data.get('status')
        if (status == CONTENT_STATUS_PUBLISHED and (not self.instance.root_node or
                                                    not self.instance.root_node.head)):
            raise forms.ValidationError('You must commit before you can publish')
        return status


class WidgyPageAdmin(PageAdmin, WidgyAdmin):
    change_form_template = 'widgy/page_builder/widgypage_change_form.html'
    form = WidgyPageAdminForm

    def get_site(self):
        return fancy_import(settings.WIDGY_MEZZANINE_SITE)

    def render_change_form(self, request, context, *args, **kwargs):
        if 'original' in context and context['original'].root_node:
            # we are rendering a change form
            obj = context['original']
            site = self.get_site()
            context['history_url'] = site.reverse(site.history_view,
                                                  kwargs={'pk': obj.root_node.pk})
        return super(WidgyPageAdmin, self).render_change_form(request, context, *args, **kwargs)


class UndeleteField(forms.ModelChoiceField):
    widget = forms.RadioSelect

    def __init__(self, *args, **kwargs):
        self.site = kwargs.pop('site')
        kwargs['queryset'] = self.get_undelete_queryset(kwargs['queryset'])
        return super(UndeleteField, self).__init__(*args, **kwargs)

    def get_undelete_queryset(self, layouts):
        """
        Version trackers that have no references and whose content type is
        allowed by our field can be restored.
        """
        VersionTracker = self.site.get_version_tracker_model()
        # Is it necessary to query on the HEAD content type _and_ the working
        # copy content type? Can a version tracker's root node content type
        # change?  If it can change, which one should be used here?
        return VersionTracker.objects.orphan().filter(
            head__root_node__content_type_id__in=layouts,
            working_copy__content_type_id__in=layouts)

    def label_from_instance(self, obj):
        url = reverse('widgy.contrib.widgy_mezzanine.views.preview',
                      kwargs={'node_pk': obj.working_copy.pk})
        return format_html('<a href="{url}">preview</a>', url=url)


class UndeletePageAdmin(WidgyPageAdmin):
    def get_form(self, request, obj=None, **kwargs):
        base = super(UndeletePageAdmin, self).get_form(request, obj, **kwargs)
        base_field = base.base_fields['root_node']
        # create a new form using an UndeleteField instead of the
        # original VersionedWidgyField
        return type(base.__class__)(base.__class__.__name__, (base,), {
            'root_node': UndeleteField(site=base_field.site,
                                       queryset=base_field.queryset,
                                       empty_label=None)
        })

    def response_add(self, request, obj, *args, **kwargs):
        resp = super(UndeletePageAdmin, self).response_add(request, obj, *args, **kwargs)
        if resp.status_code == 302 and resp['Location'].startswith('../'):
            viewname = 'admin:%s_%s_change' % (
                obj._meta.app_label,
                obj._meta.module_name)
            resp['Location'] = reverse(viewname, args=(quote(obj.pk),))
        return resp


class UndeletePage(WidgyPage):
    """
    A proxy for WidgyPage, just to allow registering WidgyPage twice with a
    different ModelAdmin.
    """
    class Meta:
        proxy = True
        app_label = WidgyPage._meta.app_label
        verbose_name = 'Restore deleted page'

    def __init__(self, *args, **kwargs):
        self._meta = super(UndeletePage, self)._meta
        return super(UndeletePage, self).__init__(*args, **kwargs)


# Remove built in Mezzanine models from the admin center
from mezzanine.pages.models import RichTextPage

admin.site.unregister(RichTextPage)

admin.site.register(WidgyPage, WidgyPageAdmin)
admin.site.register(UndeletePage, UndeletePageAdmin)
