from django.db import models
from django.core import urlresolvers

from mezzanine.pages.page_processors import processor_for
from mezzanine.pages.models import Page

class UrlconfIncludePage(Page):
    urlconf_name = models.CharField(max_length=255)

@processor_for(UrlconfIncludePage)
def include_url(request, page):
    url = request.get_full_path()
    url = url[len(page.slug) + 1:]
    view, args, kwargs = urlresolvers.resolve(
            url,
            urlconf=page.get_content_model().urlconf_name)
    return view(request, *args, **kwargs)
