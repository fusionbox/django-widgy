from widgy.site import WidgySite
from widgy.db.fields import VersionedWidgyField, WidgyField


widgy_site = WidgySite()

# This emulates importing models from a site file. It must come after
# widgy_site is defined, because widgy doesn't exist yet without the
# site.
# We have to be able to import models from the site file to use when
# checking compatibility.
VersionedWidgyField(site='tests.core_tests.widgy_config.widgy_site')
WidgyField(site='tests.core_tests.widgy_config.widgy_site')
