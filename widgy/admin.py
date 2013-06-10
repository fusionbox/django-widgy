from django.contrib.admin import ModelAdmin
from django.contrib.admin.views.main import ChangeList
from django.contrib import messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.utils.translation import ugettext_lazy as _, ugettext
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
import django

from widgy.forms import WidgyForm, ApproveForm
from widgy.utils import format_html

# BBB: Before django 1.5, only session storage supported safe string in
# messages. This is needed in order to put the undo form in messages.
HTML_IN_MESSAGES = django.VERSION >= (1, 5) or \
        settings.MESSAGE_STORAGE == 'django.contrib.messages.storage.session.SessionStorage'


class AuthorizedAdminMixin(object):
    def _has_permission(self, request, obj=None):
        try:
            self.get_site().authorize(request, self, obj)
            return True
        except PermissionDenied:
            return False

    has_add_permission = _has_permission
    has_delete_permission = _has_permission
    has_change_permission = _has_permission


class WidgyAdmin(ModelAdmin):
    """
    Base class for ModelAdmins whose models contain WidgyFields.
    """
    form = WidgyForm


class VersionCommitChangeList(ChangeList):

    # ChangeList.get_ordering allows the user to select a column
    # to order by, overriding any ordering.
    # This custom get_ordering force ordering by tracker.pk first
    # whatever column is selected. This way, we can group commit
    # per page in the template.
    def get_ordering(self, request, queryset):
        return ['tracker__pk', ] + super(VersionCommitChangeList, self).get_ordering(request, queryset) or []


class VersionCommitAdmin(AuthorizedAdminMixin, ModelAdmin):

    class Meta:
        abstract = True

    list_display = ('commit_name', 'author', 'publish_at', 'commit_preview')
    readonly_fields = ('preview', )
    list_select_related = True
    form = ApproveForm

    def get_queryset(self, request):
        try:
            qs = super(VersionCommitAdmin, self).get_queryset(request)
        except AttributeError:
            # BBB: In django 1.5 queryset changed to get_queryset
            qs = super(VersionCommitAdmin, self).queryset(request)
        return qs.get_non_approved()

    queryset = get_queryset

    def get_object(self, request, object_id):
        model = self.model
        try:
            object_id = model._meta.pk.to_python(object_id)
            return model.objects.get(pk=object_id)
        except (model.DoesNotExist, ValidationError, ValueError):
            return None

    def get_changelist(self, request, *args, **kwargs):
        return VersionCommitChangeList

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    actions = ['approve_selected']

    def get_actions(self, request):
        actions = super(VersionCommitAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def approve_selected(self, request, queryset):
        for c in queryset:
            c.approve(request.user)

        commit_count = queryset.count()
        if commit_count > 1:
            approved = _('%d commits have been approved')
        else:
            approved = _('%d commit has been approved')

        from widgy.forms import UndoApprovalsForm
        message = approved % queryset.count()
        if HTML_IN_MESSAGES:
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
        # Default save_form just do
        #   form.save(commit=false)
        # This allows the form to have access to the request, especially
        # request.user during the saving.
        return form.save(request, commit=False)

    def commit_preview(self, commit):
        url = self.get_commit_preview_url(commit)
        return format_html('<a href="{url}" class="button">{preview}</a>',
                           url=url, preview=ugettext('preview'))
    commit_preview.short_description = ''
    commit_preview.allow_tags = True

    def preview(self, commit):
        context = {
            'commit_url': self.get_commit_preview_url(commit)
        }
        return mark_safe(render_to_string('widgy/commit_preview.html',
                                          context))
    preview.short_description = _('Preview')

    def commit_name(self, commit):
        return self.get_commit_name(commit)
    commit_name.short_description = _("Commit name")

    # Override this method in subclasses
    def get_site(self):
        raise NotImplementedError('get_site should be implemented in '
                                  'in subclasses')

    # Override this method in subclasses
    def get_commit_name(self, commit):
        raise NotImplementedError('get_commit_name should be implemented '
                                  'in subclasses')

    # Override this method in subclasses
    def get_commit_preview_url(self, commit):
        raise NotImplementedError('get_commit_preview_url should be '
                                  'in subclasses')
