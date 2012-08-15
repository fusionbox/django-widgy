from widgy.contrib.list_content_widget.models import ListContentBase
from django.contrib.sites.models import Site


class SiteListCalloutContent(ListContentBase):
    model = Site
