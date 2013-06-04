from django.conf.urls import patterns, url

urlpatterns = patterns('widgy.contrib.widgy_mezzanine.views',
    url('^preview/(?P<node_pk>[^/]+)/$', 'preview'),
    url('^form/(?P<form_node_pk>[^/]*)/(?P<root_node_pk>.*)/$', 'handle_form'),
)
