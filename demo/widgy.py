from __future__ import absolute_import

from widgy.site import WidgySite
from widgy.contrib.page_builder.models import Accordion, Section

from demo.demo_widgets.models import TwoContentLayout


class DemoWidgySite(WidgySite):
    def valid_parent_of(self, parent, child_class, child=None):

        if isinstance(parent, Accordion) and isinstance(parent.get_root(), TwoContentLayout) and issubclass(child_class, Section) and len(parent.children) >= 2:
            if not child or child not in parent.children:
                return False
        return super(DemoWidgySite, self).valid_parent_of(parent, child_class, child)

widgy_site = DemoWidgySite()
