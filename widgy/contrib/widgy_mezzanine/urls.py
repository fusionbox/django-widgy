from django.conf.urls import patterns, url

urlpatterns = patterns('widgy.contrib.widgy_mezzanine.views',
    url('^preview/(?P<node_pk>[^/]+)/$', 'preview'),  # undelete
    url('^preview-page/(?P<node_pk>[^/]+)/(?P<page_pk>[^/]+)/$', 'preview'),
    url('^form-page/(?P<form_node_pk>[^/]*)/(?P<page_pk>[^/]+)/$', 'handle_form'),

    # deprecated urls for backwards compatibility with slug reversing
    url('^preview/(?P<node_pk>[^/]+)/(?P<slug>.+)/$', 'preview'),
    url('^form/(?P<form_node_pk>[^/]*)/(?P<slug>.+)/$', 'handle_form'),
)
