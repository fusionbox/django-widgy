from django.contrib.sites.models import Site

from widgy.contrib.list_content_widget.models import ListContentBase
from widgy.contrib.page_builder.models import Layout, MainContent
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
