from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('widgy.contrib.widgy_mezzanine.views',
    url('^preview/(?P<node_pk>[^/]+)/$', 'preview'),
    url('^form/(?P<node_pk>.*)/$', 'handle_form'),
)
