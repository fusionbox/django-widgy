from django.contrib.sites.models import Site

from widgy.contrib.list_content_widget.models import ListContentBase
from widgy.contrib.page_builder.models import Layout, MainContent, Accordion
from widgy import registry


class SiteListCalloutContent(ListContentBase):
    model = Site


class TwoContentLayout(Layout):
    default_children = [
        (MainContent, (), {}),
        (MainContent, (), {}),
    ]

    class Meta:
        verbose_name = 'Two Content Layout'

registry.register(TwoContentLayout)

class DemoAccordion(Accordion):
    class Meta:
        proxy = True
        verbose_name = 'Accordion'

    def valid_parent_of(self, cls, obj=None):
        if obj and obj in self.get_children():
            return True
        else:
            sup = super(DemoAccordion, self).valid_parent_of(cls)
            if isinstance(self.get_root(), TwoContentLayout):
                return sup and len(self.get_children()) < 2
            else:
                return sup

registry.unregister(Accordion)
registry.register(DemoAccordion)
