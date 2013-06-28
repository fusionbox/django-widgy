from django.conf.urls import patterns, url, include

from .widgy_config import authorized_site, widgy_site

urlpatterns = patterns('',
    url('^authenticated-widgy-site/', include(authorized_site.urls)),
    url('', include(widgy_site.urls)),
)
