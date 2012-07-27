from django.conf.urls import patterns, include, url
from django.conf import settings

urlpatterns = patterns('widgy.views',
    url('^contentpage/add/$', 'add_page'),
    url('^(?P<content_type>[A-z_]+)/(?P<id>[^/]+)/$', 'node'),

    )
