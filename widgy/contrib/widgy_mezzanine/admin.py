from __future__ import unicode_literals

from django.contrib import admin
from django.conf import settings
from django import forms
from django.core.urlresolvers import reverse
from django.contrib.admin.util import quote
from django.utils.translation import ugettext_lazy as _, ugettext
from mezzanine.pages.admin import PageAdmin
try:
    from mezzanine.pages.admin import PageAdminForm
except ImportError:
    PageAdminForm = forms.ModelForm

from mezzanine.core.models import (CONTENT_STATUS_PUBLISHED,
                                   CONTENT_STATUS_DRAFT)

from widgy.forms import WidgyFormMixin
from widgy.contrib.widgy_mezzanine import get_widgypage_model
from widgy.utils import fancy_import, format_html


WidgyPage = get_widgypage_model()


class WidgyPageAdminForm(WidgyFormMixin, PageAdminForm):
    class Meta:
        model = WidgyPage

    def __init__(self, *args, **kwargs):
        super(WidgyPageAdminForm, self).__init__(*args, **kwargs)
        self.fields['publish_date'].help_text = _(
            "If you enter a date here, the page will not be viewable on the site until then"
        )
        self.fields['expiry_date'].help_text = _(
            "If you enter a date here, the page will not be viewable after this time"
        )
        self.fields['status'].initial = CONTENT_STATUS_DRAFT

    def clean_status(self):
        status = self.cleaned_data.get('status')
        if (status == CONTENT_STATUS_PUBLISHED and (not self.instance.root_node or
                                                    not self.instance.root_node.head)):
            raise forms.ValidationError(_('You must commit before you can publish'))
        return status


class WidgyPageAdmin(PageAdmin):
    change_form_template = 'widgy/page_builder/widgypage_change_form.html'
    form = WidgyPageAdminForm


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
        #
        # Just filter based on the working copy's layout, as this allows
        # undeleting a version tracker that never got committed.
        return VersionTracker.objects.orphan().filter(
            working_copy__content_type_id__in=layouts)

    def label_from_instance(self, obj):
        url = reverse('widgy.contrib.widgy_mezzanine.views.preview',
                      kwargs={'node_pk': obj.working_copy.pk})
        return format_html('<a href="{url}">{preview}</a>', url=url, preview=ugettext('preview'))


class UndeletePageAdminMixin(object):
    def get_form(self, request, obj=None, **kwargs):
        base = super(UndeletePageAdminMixin, self).get_form(request, obj, **kwargs)
        base_field = base.base_fields['root_node']
        # create a new form using an UndeleteField instead of the
        # original VersionedWidgyField
        return type(base.__class__)(base.__class__.__name__, (base,), {
            'root_node': UndeleteField(site=base_field.site,
                                       queryset=base_field.queryset,
                                       empty_label=None,
                                       label=_('root node'))
        })

    def response_add(self, request, obj, *args, **kwargs):
        resp = super(UndeletePageAdminMixin, self).response_add(request, obj, *args, **kwargs)
        if resp.status_code == 302 and resp['Location'].startswith('../'):
            viewname = 'admin:%s_%s_change' % (
                obj._meta.app_label,
                obj._meta.module_name)
            resp['Location'] = reverse(viewname, args=(quote(obj.pk),))
        return resp


class UndeletePageAdmin(UndeletePageAdminMixin, WidgyPageAdmin):
    pass


class UndeletePage(WidgyPage):
    """
    A proxy for WidgyPage, just to allow registering WidgyPage twice with a
    different ModelAdmin.
    """
    class Meta:
        proxy = True
        app_label = WidgyPage._meta.app_label
        verbose_name = _('restore deleted page')

    def __init__(self, *args, **kwargs):
        self._meta = super(UndeletePage, self)._meta
        return super(UndeletePage, self).__init__(*args, **kwargs)


# Remove built in Mezzanine models from the admin center
from mezzanine.pages.models import RichTextPage

admin.site.unregister(RichTextPage)

admin.site.register(WidgyPage, WidgyPageAdmin)
admin.site.register(UndeletePage, UndeletePageAdmin)

if 'widgy.contrib.review_queue' in settings.INSTALLED_APPS:
    from widgy.contrib.review_queue.admin import VersionCommitAdminBase
    from widgy.contrib.review_queue.models import ReviewedVersionCommit

    class VersionCommitAdmin(VersionCommitAdminBase):
        def get_site(self):
            return fancy_import(settings.WIDGY_MEZZANINE_SITE)

    admin.site.register(ReviewedVersionCommit, VersionCommitAdmin)
