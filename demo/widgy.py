from __future__ import absolute_import

from widgy.site import WidgySite
from widgy.contrib.page_builder.models import Accordion
from widgy import registry, WidgetConfig

from demo.demo_widgets.models import TwoContentLayout


class DemoWidgySite(WidgySite):
    pass

widgy_site = DemoWidgySite()


registry.unregister(Accordion)


class DemoAccordionConfig(WidgetConfig):
    @property
    def max_number_of_children(self):
        """
        If I live in the TwoContentLayout, I only should have max
        two children.
        """
        if isinstance(self.get_root(), TwoContentLayout):
            return 2
        else:
            return self.model.max_number_of_children


registry.register(Accordion, DemoAccordionConfig)
