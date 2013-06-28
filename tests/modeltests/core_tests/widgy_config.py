from django.core.exceptions import PermissionDenied

from widgy.site import WidgySite
from widgy.db.fields import VersionedWidgyField, WidgyField


class UnauthenticatedWidgySite(WidgySite):
    def authorize(self, request, *args, **kwargs):
        if request.COOKIES.get('unauthorized_access'):
            raise PermissionDenied

widgy_site = UnauthenticatedWidgySite()
authorized_site = WidgySite()

# This emulates importing models from a site file. It must come after
# widgy_site is defined, because widgy doesn't exist yet without the
# site.
# We have to be able to import models from the site file to use when
# checking compatibility.
VersionedWidgyField(site='modeltests.core_tests.widgy_config.widgy_site')
WidgyField(site='modeltests.core_tests.widgy_config.widgy_site')
