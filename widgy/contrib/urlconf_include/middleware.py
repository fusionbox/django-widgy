import imp
import re

from django.utils.importlib import import_module
from django.conf import settings
from django.conf.urls.defaults import include, url, patterns
from django.conf.urls.i18n import i18n_patterns

from .models import UrlconfIncludePage


class PatchUrlconfMiddleware(object):
    def process_request(self, request):
        urlconf_pages = list(UrlconfIncludePage.objects.all())
        urlconf_pages.sort(key=lambda p: len(p.slug))

        root_urlconf = getattr(request, 'urlconf', settings.ROOT_URLCONF)
        if isinstance(root_urlconf, basestring):
            root_urlconf = import_module(getattr(request, 'urlconf', settings.ROOT_URLCONF))

        new_urlconf = imp.new_module('urlconf')
        new_urlconf.urlpatterns = patterns('')
        for page in urlconf_pages:
            new_urlconf.urlpatterns.extend(self.get_pattern_for_page(page))
        new_urlconf.urlpatterns.extend(root_urlconf.urlpatterns)

        if hasattr(root_urlconf, 'handler404'):
            new_urlconf.handler404 = root_urlconf.handler404
        if hasattr(root_urlconf, 'handler500'):
            new_urlconf.handler500 = root_urlconf.handler500

        request.urlconf = new_urlconf

    def get_pattern_for_page(self, page):
        return patterns('', url(r'^' + re.escape(page.slug) + '/', include(page.urlconf_name)))


class I18nPatchUrlconfMiddleware(PatchUrlconfMiddleware):
    def get_pattern_for_page(self, page):
        return i18n_patterns('', url(r'^' + re.escape(page.slug) + '/', include(page.urlconf_name)))
