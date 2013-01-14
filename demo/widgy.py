from __future__ import absolute_import

from widgy.site import WidgySite
from widgy.contrib.page_builder.models import Accordion, Section
from widgy import registry

from demo.demo_widgets.models import TwoContentLayout


class DemoWidgySite(WidgySite):
    pass

widgy_site = DemoWidgySite()
