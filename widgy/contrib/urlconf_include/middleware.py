import imp
import re
import six

# BBB Django 1.8 compatibility
import django
if django.VERSION < (1, 9):
    from django.utils.importlib import import_module
else:
    from importlib import import_module
from django.conf import settings
from django.conf.urls import include, url, patterns
from django.conf.urls.i18n import i18n_patterns
from django.core import urlresolvers

from .models import UrlconfIncludePage


def uncache_urlconf(urlconf):
    # Django's urlresolvers.get_resolver function is memoized. Since we
    # create a new urlconf module for every request, the memoize cache
    # keeps them all alive forever, causing a memory leak. Since we know
    # we're never going to need to use this specific urlconf module
    # object again, we can remove it from the cache.
    #
    # We could use urlresolvers.clear_url_caches to avoid using the
    # private `_resolver_cache`, but that might affect performance
    # because the entire cache would be cleared.
    urlresolvers.get_resolver.cache_clear()


class PatchUrlconfMiddleware(object):
    def process_request(self, request):
        root_urlconf = getattr(request, 'urlconf', settings.ROOT_URLCONF)
        if isinstance(root_urlconf, six.string_types):
            root_urlconf = import_module(root_urlconf)
        request.urlconf = self.get_urlconf(root_urlconf, self.get_pages(logged_in=request.user.is_authenticated()))
        request._patch_urlconf_middleware_urlconf = request.urlconf

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
    def get_urlconf(cls, root_urlconf, qs=None):
        if qs is None:
            qs = cls.get_pages(logged_in=False)
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
        # Our process_request may not have been called if another middleware's
        # process_request short circuited, so check first. This could still
        # leak if another middleware's process_response raises an exception.
        if response.status_code == 404 and not request.user.is_authenticated():
            # This 404 response might be because we never installed the
            # login_required urlpatterns. To be sure, try to resolve
            # the request's URL using just UrlconfIncludePages. If it
            # resolves, we know we need to redirect_to_login instead of
            # 404ing.
            try:
                # Only do something if it's a resolver 404 (the path doesn't
                # resolve originally). BBB In django >= 1.5 we can use
                # request.resolver_match.
                urlresolvers.resolve(request.get_full_path(), request.urlconf)
            except urlresolvers.Resolver404:
                empty_urlconf = imp.new_module('urlconf')
                empty_urlconf.urlpatterns = patterns('')
                urlconf = self.get_urlconf(empty_urlconf, self.get_pages(logged_in=True))
                try:
                    urlresolvers.resolve(request.get_full_path(), urlconf)
                except urlresolvers.Resolver404:
                    pass
                else:
                    from django.contrib.auth.views import redirect_to_login
                    response = redirect_to_login(request.get_full_path())
                finally:
                    uncache_urlconf(urlconf)

        if hasattr(request, 'urlconf'):
            uncache_urlconf(request.urlconf)
        if hasattr(request, '_patch_urlconf_middleware_urlconf'):
            uncache_urlconf(request._patch_urlconf_middleware_urlconf)

        return response


class I18nPatchUrlconfMiddleware(PatchUrlconfMiddleware):
    @classmethod
    def get_pattern_for_page(cls, page):
        return i18n_patterns('', url(r'^' + re.escape(page.slug) + '/', include(page.urlconf_name)))
