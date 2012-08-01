from django.conf.urls import patterns, include, url
from django.conf import settings

urlpatterns = patterns('widgy.views',
    #url('^contentpage/add/$', 'add_page'),
    #url('^contentpage/(?P<object_id>[^/]+)/$', 'change_page'),
    url('^node/$', 'create_node'),
    url('^node/(?P<node_pk>[^/]+)/$', 'node'),
    url('^node/(?P<node_pk>[^/]+)/available-children-recursive/$', 'children'),
    url('^widgets/$', 'children'),
    url('^contents/(?P<app_label>[A-z_-]+)/(?P<object_name>[A-z_-]+)/(?P<object_pk>[^/]+)/$', 'content'),
    )
