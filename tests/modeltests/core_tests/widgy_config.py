from django.core.exceptions import PermissionDenied

from widgy.site import WidgySite


class UnauthenticatedWidgySite(WidgySite):
    def authorize(self, request, *args, **kwargs):
        if request.COOKIES.get('unauthorized_access'):
            raise PermissionDenied


widgy_site = UnauthenticatedWidgySite()
