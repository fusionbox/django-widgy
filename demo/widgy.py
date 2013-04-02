from __future__ import absolute_import

from widgy.site import WidgySite
from widgy.contrib.page_builder.models import Accordion, Section
from widgy.contrib.widgy_i18n.models import I18NLayout
from widgy import registry

from demo.demo_widgets.models import TwoContentLayout


class DemoWidgySite(WidgySite):
    def valid_parent_of(self, parent, child_class, obj=None):
        if isinstance(parent, I18NLayout):
            return True

widgy_site = DemoWidgySite()
