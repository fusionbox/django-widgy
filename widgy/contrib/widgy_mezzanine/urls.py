from django.conf.urls import url

import widgy.contrib.widgy_mezzanine.views

urlpatterns = [
    url('^preview/(?P<node_pk>[^/]+)/$',
        widgy.contrib.widgy_mezzanine.views.preview,
        name='widgy.contrib.widgy_mezzanine.views.preview'),  # undelete
    url('^preview-page/(?P<node_pk>[^/]+)/(?P<page_pk>[^/]+)/$',
        widgy.contrib.widgy_mezzanine.views.preview,
        name='widgy.contrib.widgy_mezzanine.views.preview'),
    url('^form-page/(?P<form_node_pk>[^/]*)/(?P<page_pk>[^/]+)/$',
        widgy.contrib.widgy_mezzanine.views.handle_form,
        name='widgy.contrib.widgy_mezzanine.views.handle_form'),
    # deprecated urls for backwards compatibility with slug reversing
    url('^preview/(?P<node_pk>[^/]+)/(?P<slug>.+)/$',
        widgy.contrib.widgy_mezzanine.views.preview,
        name='widgy.contrib.widgy_mezzanine.views.preview'),
    url('^form/(?P<form_node_pk>[^/]*)/(?P<slug>.+)/$',
        widgy.contrib.widgy_mezzanine.views.handle_form,
        name='widgy.contrib.widgy_mezzanine.views.handle_form'),
]
