from django.conf.urls import patterns, url, include
from django.contrib import admin
from .widgy_config import widgy_site

urlpatterns = patterns('',
    url('', include(widgy_site.urls)),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin/widgy/', include(widgy_site.urls)),
    url(r'^widgy/', include('widgy.contrib.widgy_mezzanine.urls')),
    url(r'^', include('mezzanine.urls')),
    url(r'^mazzaninehome/$', 'mezzanine.pages.views.page', name='home'),
)
