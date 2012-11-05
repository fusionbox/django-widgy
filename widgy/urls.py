from django.conf.urls import patterns, include, url
from django.conf import settings

urlpatterns = patterns('widgy.views',
    url('^node/$', 'node'),
    url('^node/(?P<node_pk>[^/]+)/$', 'node'),
    url('^node/(?P<node_pk>[^/]+)/available-children/$', 'children'),
    url('^node/(?P<node_pk>[^/]+)/available-children-recursive/$', 'recursive_children'),
    url('^widgets/$', 'children'),
    url('^contents/(?P<app_label>[A-z_-]+)/(?P<object_name>[A-z_-]+)/(?P<object_pk>[^/]+)/$', 'content'),
    )
