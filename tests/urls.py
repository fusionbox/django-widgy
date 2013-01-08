from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url('^admin/widgy/', include('widgy.urls')),
    url("^admin/", include(admin.site.urls)),
)
