from django.contrib.admin import ModelAdmin
from django.core.exceptions import PermissionDenied

from widgy.forms import WidgyForm


class AuthorizedAdminMixin(object):
    def _has_permission(self, request, obj=None):
        try:
            self.get_site().authorize_view(request, self)
            return True
        except PermissionDenied:
            return False

    def has_add_permission(self, request, obj=None):
        return super(AuthorizedAdminMixin, self).has_add_permission(request, obj) and self._has_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        return super(AuthorizedAdminMixin, self).has_change_permission(request, obj) and self._has_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return super(AuthorizedAdminMixin, self).has_delete_permission(request, obj) and self._has_permission(request, obj)


class WidgyAdmin(ModelAdmin):
    """
    Base class for ModelAdmins whose models contain WidgyFields.
    """
    form = WidgyForm
