import imp
import re

from django.utils.importlib import import_module
from django.conf import settings
from django.conf.urls import include, url, patterns
from django.conf.urls.i18n import i18n_patterns
from django.core import urlresolvers

from .models import UrlconfIncludePage


class PatchUrlconfMiddleware(object):
    def process_request(self, request):
        root_urlconf = getattr(request, 'urlconf', settings.ROOT_URLCONF)
        if isinstance(root_urlconf, basestring):
            root_urlconf = import_module(root_urlconf)
        request.urlconf = self.get_urlconf(root_urlconf, self.get_pages(logged_in=request.user.is_authenticated()))

    @classmethod
    def get_pattern_for_page(cls, page):
        return patterns('', url(r'^' + re.escape(page.slug) + '/', include(page.urlconf_name)))

    @classmethod
    def get_pages(cls, logged_in):
        qs = UrlconfIncludePage.objects.published()
        if not logged_in:
            qs = qs.exclude(login_required=True)
        return qs

    @classmethod
    def get_urlconf(cls, root_urlconf, qs):
        urlconf_pages = sorted(qs, key=lambda p: len(p.slug))

        new_urlconf = imp.new_module('urlconf')
        new_urlconf.urlpatterns = patterns('')
        for page in urlconf_pages:
            new_urlconf.urlpatterns.extend(cls.get_pattern_for_page(page))
        new_urlconf.urlpatterns.extend(root_urlconf.urlpatterns)

        if hasattr(root_urlconf, 'handler404'):
            new_urlconf.handler404 = root_urlconf.handler404
        if hasattr(root_urlconf, 'handler500'):
            new_urlconf.handler500 = root_urlconf.handler500

        return new_urlconf

    def process_response(self, request, response):
        if response.status_code == 404 and not request.user.is_authenticated():
            # This 404 response might be because we never installed the
            # login_required urlpatterns. To be sure, try to resolve
            # the request's URL using just UrlconfIncludePages. If it
            # resolves, we know we need to redirect_to_login instead of
            # 404ing.
            empty_urlconf = imp.new_module('urlconf')
            empty_urlconf.urlpatterns = patterns('')
            urlconf = self.get_urlconf(empty_urlconf, self.get_pages(logged_in=True))
            try:
                urlresolvers.resolve(request.get_full_path(), urlconf)
            except urlresolvers.Resolver404:
                pass
            else:
                from django.contrib.auth.views import redirect_to_login
                return redirect_to_login(request.get_full_path())
        return response


class I18nPatchUrlconfMiddleware(PatchUrlconfMiddleware):
    @classmethod
    def get_pattern_for_page(cls, page):
        return i18n_patterns('', url(r'^' + re.escape(page.slug) + '/', include(page.urlconf_name)))
