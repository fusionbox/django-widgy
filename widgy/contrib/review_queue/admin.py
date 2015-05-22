from __future__ import unicode_literals

from django.contrib.admin import ModelAdmin
from django.contrib.admin.views.main import ChangeList
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _, ungettext
from django.utils.html import format_html
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.encoding import force_text

from widgy.admin import AuthorizedAdminMixin

from .forms import ApproveForm
from .models import ReviewedVersionTracker


class VersionCommitChangeList(ChangeList):
    # ChangeList.get_ordering allows the user to select a column
    # to order by, overriding any ordering.
    # This custom get_ordering force ordering by tracker.pk first
    # whatever column is selected. This way, we can group commit
    # per page in the template.
    def get_ordering(self, request, queryset):
        return ['tracker__pk', ] + super(VersionCommitChangeList, self).get_ordering(request, queryset) or []

    def get_results(self, request):
        ret = super(VersionCommitChangeList, self).get_results(request)

        # Manually prefetch owners. We can't do a normal
        # ReviewedVersionCommit.objects.prefetch_related('tracker__widgypage_set')
        # because ReviewedVersionCommit.tracker is a VersionTracker (which
        # doesn't have the reverse relationship), not a ReviewedVersionTracker.
        trackers = ReviewedVersionTracker.objects.prefetch_related(
            *ReviewedVersionTracker.get_owner_related_names()
        ).in_bulk(
            set(commit.tracker_id for commit in self.result_list)
        )
        for commit in self.result_list:
            commit.tracker = trackers[commit.tracker_id]

        return ret


class VersionCommitAdminBase(AuthorizedAdminMixin, ModelAdmin):
    list_display = ('commit_name', 'author', 'publish_at', 'commit_preview')
    readonly_fields = ('preview', )
    list_select_related = True
    form = ApproveForm
    actions = ['approve_selected']

    def get_queryset(self, request):
        qs = super(VersionCommitAdminBase, self).get_queryset(request)
        if not request.resolver_match.args:
            # This means we're on the changelist page, and shouldn't see
            # unapproved commits. We only do this for the changelist, because
            # you should be able to view the detail page for an approved
            # commit.
            qs = qs.unapproved()
        return qs.select_related('author', 'root_node')
    queryset = get_queryset

    def get_changelist(self, request, *args, **kwargs):
        return VersionCommitChangeList

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super(VersionCommitAdminBase, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def approve_selected(self, request, queryset):
        for c in queryset:
            c.approve(request.user)

        commit_count = queryset.count()

        message = ungettext(
            '%d commit has been approved.',
            '%d commits have been approved.',
            commit_count
        ) % (commit_count,)

        from .forms import UndoApprovalsForm
        message = format_html(
            '{0} {1}',
            message,
            UndoApprovalsForm(
                initial={
                    'actions': [c.pk for c in queryset],
                    'referer': request.path,
                }
            ).render(request, self.get_site())
        )

        messages.info(request, message, extra_tags='safe')
    approve_selected.short_description = _('Approve selected commits')

    def save_form(self, request, form, change):
        # Default save_form just does
        #   form.save(commit=false)
        # This allows the form to have access to the request, especially
        # request.user during the saving.
        return form.save(request, commit=False)

    def commit_name(self, commit):
        assert isinstance(commit.tracker, ReviewedVersionTracker), (
            "We rely on the VersionCommitChangeList to set commit.tracker"
            " to a ReviewedVersionTracker."
        )
        return ', '.join(force_text(owner) for owner in commit.tracker.owners)
    commit_name.short_description = _("Commit name")

    def commit_preview(self, commit):
        res = []
        for owner in commit.tracker.owners:
            if hasattr(owner, 'get_action_links'):
                for link in owner.get_action_links(commit.root_node):
                    res.append(format_html('<a href="{url}">{text}</a>', **link))
        return ' '.join(res)
    commit_preview.short_description = ''
    commit_preview.allow_tags = True

    def preview(self, commit):
        context = {
            'owners': ReviewedVersionTracker.objects.get(pk=commit.tracker_id).owners,
            'node': commit.root_node,
        }
        return mark_safe(render_to_string('review_queue/commit_preview.html',
                                          context))
    preview.short_description = _('Preview')

    # Override this method in subclasses
    def get_site(self):
        raise NotImplementedError('get_site should be implemented in subclasses')
