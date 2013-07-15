from django.conf.urls import patterns, url

urlpatterns = patterns('widgy.contrib.widgy_mezzanine.views',
    url('^preview/(?P<node_pk>[^/]+)/$', 'preview'),  # undelete
    url('^preview/(?P<node_pk>[^/]+)/(?P<slug>.+)/$', 'preview'),
    url('^form/(?P<form_node_pk>[^/]*)/(?P<slug>.+)/$', 'handle_form'),
)
