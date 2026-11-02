from django.urls import re_path

import widgy.contrib.widgy_mezzanine.views

urlpatterns = [
    re_path('^preview/(?P<node_pk>[^/]+)/$',
        widgy.contrib.widgy_mezzanine.views.preview,
        name='widgy.contrib.widgy_mezzanine.views.preview'),  # undelete
    re_path('^preview-page/(?P<node_pk>[^/]+)/(?P<page_pk>[^/]+)/$',
        widgy.contrib.widgy_mezzanine.views.preview,
        name='widgy.contrib.widgy_mezzanine.views.preview'),
    re_path('^form-page/(?P<form_node_pk>[^/]*)/(?P<page_pk>[^/]+)/$',
        widgy.contrib.widgy_mezzanine.views.handle_form,
        name='widgy.contrib.widgy_mezzanine.views.handle_form'),
    # deprecated urls for backwards compatibility with slug reversing
    re_path('^preview/(?P<node_pk>[^/]+)/(?P<slug>.+)/$',
        widgy.contrib.widgy_mezzanine.views.preview,
        name='widgy.contrib.widgy_mezzanine.views.preview'),
    re_path('^form/(?P<form_node_pk>[^/]*)/(?P<slug>.+)/$',
        widgy.contrib.widgy_mezzanine.views.handle_form,
        name='widgy.contrib.widgy_mezzanine.views.handle_form'),
]
