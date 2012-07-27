from django.conf.urls import patterns, include, url
from django.conf import settings

urlpatterns = patterns('widgy.views',
    url('^contentpage/add/$', 'add_page'),
    url('^contentpage/(?P<object_id>[^/]+)/$', 'change_page'),
    url('^node/(?P<node_pk>[^/]+)/$', 'node'),
    url('^(?P<object_name>[A-z_]+)/(?P<object_pk>[^/]+)/$', 'content'),

    )
