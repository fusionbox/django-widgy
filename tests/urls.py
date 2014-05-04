from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()


def dummy_view(*args, **kwargs):
    pass


urlpatterns = patterns('',
    url('^core_tests/', include('modeltests.core_tests.urls')),
    url("^admin/", include(admin.site.urls)),
    url('^widgy-mezzanine/', include('widgy.contrib.widgy_mezzanine.urls')),
    # mezzanine.pages.views.page reverses the 'home' url.
    url('^$', dummy_view, name='home'),
)
