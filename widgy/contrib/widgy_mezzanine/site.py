from mezzanine.utils.sites import current_site_id, has_site_permission
from widgy.models import Content


class MultiSitePermissionMixin(object):
    def _can_edit_content(self, request, obj):
        if isinstance(obj, Content):
            owners = obj.get_root().node.versiontracker_set.get().owners
            any_owner_in_current_site = any(current_site_id() == o.site_id for o in owners)
            return has_site_permission(request.user) and any_owner_in_current_site
        else:
            return True

    def has_add_permission(self, request, parent, created_obj_cls):
        if not self._can_edit_content(request, parent):
            return False
        return super(MultiSitePermissionMixin, self).has_add_permission(
            request, parent, created_obj_cls)

    def has_change_permission(self, request, obj_or_class):
        if not self._can_edit_content(request, obj_or_class):
            return False
        return super(MultiSitePermissionMixin, self).has_change_permission(request, obj_or_class)

    def has_delete_permission(self, request, obj_or_class):
        if not all(self._can_edit_content(request, o) for o in obj_or_class.depth_first_order()):
            return False
        return super(MultiSitePermissionMixin, self).has_delete_permission(request, obj_or_class)
