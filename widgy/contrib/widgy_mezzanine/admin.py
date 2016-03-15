from __future__ import unicode_literals

from django.contrib import admin
from django.conf import settings
from django.conf.urls import url
from django import forms
from django.core.urlresolvers import reverse
try:
    from django.contrib.admin.utils import quote
except ImportError:  # < Django 1.8
    from django.contrib.admin.util import quote
from django.utils.translation import ugettext_lazy as _, ugettext, ungettext
from django.utils.html import format_html
from django.utils import timezone
from django.contrib import messages
from django.db.models.signals import post_save
from django.db.models import Min, Q
from django.contrib.sites.models import Site

from mezzanine.utils.sites import current_site_id
from mezzanine.pages.admin import PageAdmin
try:
    from mezzanine.pages.admin import PageAdminForm
except ImportError:
    PageAdminForm = forms.ModelForm

from mezzanine.core.models import (CONTENT_STATUS_PUBLISHED,
                                   CONTENT_STATUS_DRAFT)

from widgy.forms import WidgyFormMixin, VersionedWidgyWidget
from widgy.contrib.widgy_mezzanine import get_widgypage_model
from widgy.contrib.widgy_mezzanine.views import ClonePageView, UnpublishView
from widgy.contrib.page_builder.admin import CalloutAdmin
from widgy.contrib.page_builder.models import Callout
from widgy.contrib.form_builder.admin import FormAdmin
from widgy.contrib.form_builder.models import Form
from widgy.db.fields import get_site
from widgy.models import Node
from widgy.admin import WidgyAdmin


WidgyPage = get_widgypage_model()


if 'widgy.contrib.review_queue' in settings.INSTALLED_APPS:
    REVIEW_QUEUE_INSTALLED = True
    from widgy.contrib.review_queue.site import ReviewedWidgySite
else:
    REVIEW_QUEUE_INSTALLED = False


class PageVersionedWidgyWidget(VersionedWidgyWidget):
    template_name = 'widgy/widgy_mezzanine/versioned_widgy_field.html'


class WidgyPageAdminForm(WidgyFormMixin, PageAdminForm):
    class Meta:
        model = WidgyPage
        widgets = {
            'root_node': PageVersionedWidgyWidget,
        }
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(WidgyPageAdminForm, self).__init__(*args, **kwargs)
        self.fields['publish_date'].help_text = _(
            "If you enter a date here, the page will not be viewable on the site until then"
        )
        self.fields['expiry_date'].help_text = _(
            "If you enter a date here, the page will not be viewable after this time"
        )
        if self.instance.pk is None:
            self.instance.status = CONTENT_STATUS_DRAFT


# the status of a page before it's created, on the add page
CONTENT_STATUS_EMBRYO = 0

class WidgyPageAdmin(PageAdmin):
    change_form_template = 'widgy/widgy_mezzanine/widgypage_change_form.html'
    form = WidgyPageAdminForm
    readonly_fields = ['status']

    unreviewed_buttons = {
        CONTENT_STATUS_EMBRYO    : [('_continue', _('Save'))],
        CONTENT_STATUS_DRAFT     : [('_continue', _('Save as Draft')),
                                    ('_save_and_commit', _('Publish'))],
        CONTENT_STATUS_PUBLISHED : [('_save_and_commit', _('Publish Changes'))],
    }
    reviewed_buttons = {
        (CONTENT_STATUS_EMBRYO, False)    : [('_continue', _('Save'))],
        (CONTENT_STATUS_EMBRYO, True)     : [('_continue', _('Save'))],
        (CONTENT_STATUS_DRAFT, False)     : [('_continue', _('Save as Draft')),
                                             ('_save_and_commit', _('Submit for Review'))],
        (CONTENT_STATUS_DRAFT, True)      : [('_continue', _('Save as Draft')),
                                             ('_save_and_commit', _('Submit for Review')),
                                             ('_save_and_approve', _('Publish'))],
        (CONTENT_STATUS_PUBLISHED, False) : [('_save_and_commit', _('Submit for Review'))],
        (CONTENT_STATUS_PUBLISHED, True)  : [('_save_and_commit', _('Submit for Review')),
                                             ('_save_and_approve', _('Publish Changes'))],
    }

    def get_urls(self):
        clone_view = ClonePageView.as_view(
            model=self.model,
            has_permission=self.has_add_permission,
        )
        unpublish_view = UnpublishView.as_view(
            model=self.model,
            has_change_permission=self.has_change_permission,
        )
        return [
            url(
                '^(.+)/clone/$',
                self.admin_site.admin_view(clone_view),
                name='widgy_mezzanine_widgypage_clone',
            ),
            url(
                '^(.+)/unpublish/$',
                self.admin_site.admin_view(unpublish_view),
                name='widgy_mezzanine_widgypage_unpublish',
            ),
        ] + super(WidgyPageAdmin, self).get_urls()

    def _save_and_commit(self, request, obj):
        site = self.get_site()
        commit_model = site.get_version_tracker_model().commit_model
        if not site.has_add_permission(request, obj, commit_model):
            messages.error(request, _("You don't have permission to commit."))
        else:
            if obj.root_node.has_changes():
                obj.root_node.commit(user=request.user)
            elif self.has_review_queue:
                messages.warning(request, _("There was nothing to submit for review."))

            if not self.has_review_queue:
                obj.status = CONTENT_STATUS_PUBLISHED
            # else:
                # If we are reviewed, we'll have to wait for approval.
                # Handled by the publish_page_on_approve signal.

    def _save_and_approve(self, request, obj):
        site = self.get_site()
        commit_model = site.get_version_tracker_model().commit_model
        if not site.has_add_permission(request, obj, commit_model) or \
                not site.has_change_permission(request, commit_model):
            messages.error(request, _("You don't have permission to approve commits."))
        else:
            if obj.root_node.has_changes():
                obj.root_node.commit(request.user)
            # If we had changes, `head` is the same commit we just created.
            # If we didn't need to create a commit, we want to publish the
            # most recent one instead.
            obj.root_node.head.reviewedversioncommit.approve(request.user)
            obj.root_node.head.reviewedversioncommit.save()
            obj.status = CONTENT_STATUS_PUBLISHED

    def save_model(self, request, obj, form, change):
        if '_save_and_commit' in request.POST:
            self._save_and_commit(request, obj)
        elif '_save_and_approve' in request.POST and self.has_review_queue:
            self._save_and_approve(request, obj)
        request.POST['_continue'] = True
        super(WidgyPageAdmin, self).save_model(request, obj, form, change)

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None, *args, **kwargs):
        if not add:
            unapproved = 0
            future = 0
            for commit in obj.root_node.get_history_list():
                if obj.root_node.commit_is_ready(commit):
                    # got to the currently-published commit
                    break
                if self.has_review_queue and not commit.reviewedversioncommit.is_approved:
                    unapproved += 1
                if not commit.is_published:
                    future += 1
            if unapproved:
                messages.warning(request, ungettext(
                    "There is one unreviewed commit for this page.",
                    "There are {count} unreviewed commits for this page.",
                    unapproved
                ).format(count=unapproved))
            if future:
                messages.warning(request, ungettext(
                    "There is one future-scheduled commit.",
                    "There are {count} future-scheduled commits.",
                    future
                ).format(count=future))

        site = self.get_site()
        if add:
            status = CONTENT_STATUS_EMBRYO
        else:
            status = obj.status
        if self.has_review_queue:
            commit_model = site.get_version_tracker_model().commit_model
            can_approve = site.has_change_permission(request, commit_model)
            context['save_buttons'] = self.reviewed_buttons[(status, can_approve)]
        else:
            context['save_buttons'] = self.unreviewed_buttons[status]
        if not add:
            context['history_url'] = site.reverse(site.history_view, kwargs={'pk': obj.root_node_id})
        return super(WidgyPageAdmin, self).render_change_form(request, context, add, change, form_url, obj, *args, **kwargs)

    @property
    def has_review_queue(self):
        return REVIEW_QUEUE_INSTALLED and isinstance(self.get_site(), ReviewedWidgySite)

    def get_site(self):
        return get_site(settings.WIDGY_MEZZANINE_SITE)


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
                obj._meta.model_name)
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


admin.site.register(WidgyPage, WidgyPageAdmin)
admin.site.register(UndeletePage, UndeletePageAdmin)


def publish_page_on_approve(sender, instance, created, **kwargs):
    site = get_site(settings.WIDGY_MEZZANINE_SITE)

    pages = WidgyPage.objects.filter(
        root_node=instance.tracker,
    )
    if instance.is_approved:
        pages = pages.filter(
            Q(publish_date__gte=instance.publish_at) |
            Q(status=CONTENT_STATUS_DRAFT)
        ).update(
            status=CONTENT_STATUS_PUBLISHED,
            publish_date=instance.publish_at,
        )
    elif not site.get_version_tracker_model().objects.filter(pk=instance.tracker.pk).published().exists():
        # unaproving a commit, and there are no other currently published commits
        CommitModel = site.get_version_tracker_model().commit_model
        beginning_of_validity = CommitModel.objects.approved().filter(
            tracker_id=instance.tracker.pk,
            publish_at__gt=timezone.now(),
        ).aggregate(min=Min('publish_at'))['min']
        if beginning_of_validity is not None:
            # There's a scheduled commit, move publish_date of the page forward
            # up to the publish_at of the commit.
            pages.update(
                publish_date=beginning_of_validity,
                status=CONTENT_STATUS_PUBLISHED,
            )
        else:
            # no other published commits at all, page needs to be unpublished
            pages.update(
                status=CONTENT_STATUS_DRAFT,
            )


class MultiSiteFormAdmin(FormAdmin):
    def get_queryset(self, request):
        version_tracker_model = self.get_site().get_version_tracker_model()
        site_pages = version_tracker_model.objects.filter(widgypage__site_id=current_site_id())
        site_nodes = Node.objects.filter(versiontracker__in=site_pages)

        # This query seems like it could get slow. If that's the case,
        # something along these lines might be helpful:
        # Node.objects.all().extra(
        #     tables=[
        #         '"widgy_node" AS "root"',
        #         'widgy_versiontracker',
        #         'widgy_mezzanine_widgypage',
        #         'pages_page',
        #     ],
        #     where=[
        #         'root.path = SUBSTR(widgy_node.path, 1, 4)',
        #         'widgy_versiontracker.id = widgy_mezzanine_widgypage.root_node_id',
        #         'pages_page.id = widgy_mezzanine_widgypage.page_ptr_id',
        #         'pages_page.site_id = 1',
        #     ]
        # )
        qs = super(MultiSiteFormAdmin, self).get_queryset(request).filter(
            _nodes__path__path_root__in=site_nodes.values_list('path'),
        )
        return qs

    def get_site(self):
        return get_site(settings.WIDGY_MEZZANINE_SITE)

admin.site.unregister(Form)
admin.site.register(Form, MultiSiteFormAdmin)


class MultiSiteCalloutAdmin(WidgyAdmin):
    def get_site_list(self, request):
        if not hasattr(request, '_site_list'):
            # Mezzanine has a weird data model for site permissions. This optimizes the query into
            # one single SQL statement. This also avoids raising an ObjectDoesNotExist error in case
            # a user does not have a sitepermission object.
            request._site_list = Site.objects.filter(sitepermission__user=request.user)
        return request._site_list

    def get_fields(self, request, obj=None):
        site_list = self.get_site_list(request)
        if request.user.is_superuser or len(site_list) > 1:
            return ('name', 'site', 'root_node')
        else:
            return ('name', 'root_node')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'site' and not request.user.is_superuser:
            # See MultiSiteCalloutAdmin.get_fields() about this query
            kwargs['queryset'] = self.get_site_list(request)

            # Non superusers have to select a site, otherwise the callout will be global.
            kwargs['required'] = True
        return super(MultiSiteCalloutAdmin, self).formfield_for_foreignkey(
            db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if not change:
            site_list = self.get_site_list(request)
            if len(site_list) == 1:
                obj.site = site_list.get()
        return super(MultiSiteCalloutAdmin, self).save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super(MultiSiteCalloutAdmin, self).get_queryset(request)
        if not (request.user.is_superuser or (request.user.is_staff and Site.objects.count() == 1)):
            qs = qs.filter(site__sitepermission__user=request.user)
        return qs

admin.site.unregister(Callout)
admin.site.register(Callout, MultiSiteCalloutAdmin)

if REVIEW_QUEUE_INSTALLED:
    from widgy.contrib.review_queue.admin import VersionCommitAdminBase
    from widgy.contrib.review_queue.models import ReviewedVersionCommit, ReviewedVersionTracker

    class VersionCommitAdmin(VersionCommitAdminBase):
        def get_site(self):
            return get_site(settings.WIDGY_MEZZANINE_SITE)

        def get_queryset(self, request):
            qs = super(VersionCommitAdmin, self).get_queryset(request)

            if not request.user.is_superuser:
                sites = Site.objects.filter(sitepermission__user=request.user)
                qs = qs.filter(
                    tracker__in=ReviewedVersionTracker.objects.filter(widgypage__site__in=sites)
                )

            return qs

    admin.site.register(ReviewedVersionCommit, VersionCommitAdmin)

    site = get_site(settings.WIDGY_MEZZANINE_SITE)

    if isinstance(site, ReviewedWidgySite):
        # In the tests, review_queue is installed but a ReviewedWidgySite might
        # not be in use.
        post_save.connect(publish_page_on_approve, sender=site.get_version_tracker_model().commit_model)
