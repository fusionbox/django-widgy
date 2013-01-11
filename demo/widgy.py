from __future__ import absolute_import

from widgy.site import WidgySite


class DemoWidgySite(WidgySite):
    def valid_parent_of(self, parent, child_class, child=None):
        from widgy.contrib.page_builder.models import Accordion, Section
        from demo.demo_widgets.models import TwoContentLayout

        if isinstance(parent, Accordion) and isinstance(parent.get_root(), TwoContentLayout) and issubclass(child_class, Section) and len(parent.children) >= 2:
            return False
        return super(DemoWidgySite, self).valid_parent_of(parent, child_class, child)

widgy_site = DemoWidgySite()
