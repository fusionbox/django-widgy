from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url('^core_tests/', include('modeltests.core_tests.urls')),
    url("^admin/", include(admin.site.urls)),
    url('^widgy-mezzanine/', include('widgy.contrib.widgy_mezzanine.urls')),
)
