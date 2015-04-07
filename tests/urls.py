import django
from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin

if django.VERSION < (1, 7):
    admin.autodiscover()


def dummy_view(*args, **kwargs):
    pass


urlpatterns = patterns('',
    url('^core_tests/', include('tests.core_tests.urls')),
    url("^admin/", include(admin.site.urls)),
    # mezzanine.pages.views.page reverses the 'home' url.
    url('^$', dummy_view, name='home'),
)

if 'widgy.contrib.widgy_mezzanine' in settings.INSTALLED_APPS:
    urlpatterns += [
        url('^widgy-mezzanine/', include('widgy.contrib.widgy_mezzanine.urls')),
        url('^mezzanine/', include('mezzanine.urls')),
    ]
