import imp

import django
from django.test import TestCase
from django.test.client import RequestFactory
from django.utils.decorators import decorator_from_middleware
from django.http import HttpResponse, HttpResponseNotFound
from django.core import urlresolvers
from django.contrib.auth.models import AnonymousUser
from django.conf.urls import include, url, patterns

from widgy.contrib.urlconf_include.middleware import PatchUrlconfMiddleware
from widgy.contrib.urlconf_include.models import UrlconfIncludePage

patch_decorator = decorator_from_middleware(PatchUrlconfMiddleware)


@patch_decorator
def plain_view(request):
    return HttpResponse('')


@patch_decorator
def view_that_resolves(request, login_url):
    # Use request.urlconf because we're mocking everything. BaseHandler
    # would call set_urlconf if we were making a real request.
    from django.contrib.auth.views import login as login_view
    match = urlresolvers.resolve(login_url, request.urlconf)
    assert match.func == login_view
    return HttpResponse('')

@patch_decorator
def view_that_reverses(request, desired):
    assert urlresolvers.reverse('login', request.urlconf) == desired
    return HttpResponse('')

@patch_decorator
def view_not_found(request):
    return HttpResponseNotFound('')

@patch_decorator
def view_that_switches_urlconf(request, login_url):
    urlresolvers.resolve(login_url, request.urlconf)

    new_urlconf = imp.new_module('urlconf')
    new_urlconf.urlpatterns = patterns('', url(r'^bar/', include('django.contrib.auth.urls')))
    request.urlconf = new_urlconf

    urlresolvers.resolve('/bar/login/', request.urlconf)

    return HttpResponse('')


class TestMiddleware(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    if django.VERSION > (1, 7):
        def resolver_cache_size(self):
            return urlresolvers.get_resolver.cache_info().currsize
    else:
        def resolver_cache_size(self):
            return len(urlresolvers._resolver_cache)

    def get_request(self, path='/'):
        r = self.factory.get(path)
        r.user = AnonymousUser()
        return r

    def test_noresolve(self):
        # It's helpful to test a view that does no resolving, because
        # uncache_urlconf needs to catch KeyError.
        plain_view(self.get_request())

    def do_test_memory_leak(self, doit):
        UrlconfIncludePage.objects.create(
            slug='foo',
            urlconf_name='django.contrib.auth.urls',
        )

        # warmup
        doit()
        doit()

        n = self.resolver_cache_size()
        doit()
        doit()
        n_after = self.resolver_cache_size()

        self.assertEqual(n, n_after)

    def test_memory_leak(self):
        def doit():
            view_that_resolves(self.get_request(), login_url='/foo/login/')
        self.do_test_memory_leak(doit)

    def test_memory_leak_404(self):
        def doit():
            view_not_found(self.get_request('/asdf/asdfasdf/'))
        self.do_test_memory_leak(doit)

    def test_memory_leak_urlconf_replaced(self):
        def doit():
            view_that_switches_urlconf(self.get_request(), '/foo/login/')
        self.do_test_memory_leak(doit)

    def test_change_url(self):
        page = UrlconfIncludePage.objects.create(
            slug='foo',
            urlconf_name='django.contrib.auth.urls',
        )

        view_that_resolves(self.get_request(), login_url='/foo/login/')
        view_that_reverses(self.get_request(), desired='/foo/login/')

        page.slug = 'bar'
        page.save()

        view_that_reverses(self.get_request(), desired='/bar/login/')
        view_that_resolves(self.get_request(), login_url='/bar/login/')

    def test_login_required(self):
        UrlconfIncludePage.objects.create(
            slug='foo',
            urlconf_name='django.contrib.auth.urls',
            login_required=True,
        )

        with self.assertRaises(urlresolvers.Resolver404):
            view_that_resolves(self.get_request(), login_url='404')

        r = self.get_request()
        r.user.is_authenticated = lambda: True
        view_that_resolves(r, login_url='/foo/login/')

    def test_login_redirect(self):
        UrlconfIncludePage.objects.create(
            slug='foo',
            urlconf_name='django.contrib.auth.urls',
            login_required=True,
        )

        # request for good url redirects to login
        r = self.get_request('/foo/login/')
        resp = view_not_found(r)
        self.assertEqual(resp.status_code, 302)

        # request for 404 url stays 404
        r = self.get_request('/foo/nonexistentasdf/')
        resp = view_not_found(r)
        self.assertEqual(resp.status_code, 404)

    def test_login_required_legit_404_shouldnt_redirect(self):
        """
        We should only redirect to login if there was no urlpattern that
        matched, not for other types of 404s.
        """
        UrlconfIncludePage.objects.create(
            slug='foo',
            urlconf_name='django.contrib.auth.urls',
            login_required=False,
        )

        r = self.get_request('/foo/login/')
        resp = view_not_found(r)
        self.assertEqual(resp.status_code, 404)
