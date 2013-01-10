from django.conf.urls import patterns, url, include

from .widgy_config import widgy_site

urlpatterns = patterns('',
    url('', include(widgy_site.urls)),
)
