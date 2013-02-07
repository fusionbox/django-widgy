from django.core.exceptions import PermissionDenied

from widgy.site import WidgySite
from widgy.db.fields import VersionedWidgyField, WidgyField

class UnauthenticatedWidgySite(WidgySite):
    def authorize(self, request, *args, **kwargs):
        if request.COOKIES.get('unauthorized_access'):
            raise PermissionDenied

# this is a test case! These fields must lazily import site
VersionedWidgyField(site='modeltests.core_tests.widgy_config.widgy_site')
WidgyField(site='modeltests.core_tests.widgy_config.widgy_site')

widgy_site = UnauthenticatedWidgySite()
