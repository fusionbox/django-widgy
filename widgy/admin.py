from django.contrib.admin import ModelAdmin
from django.core.exceptions import PermissionDenied

from widgy.forms import WidgyForm


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
