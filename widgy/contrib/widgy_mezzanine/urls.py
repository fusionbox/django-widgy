from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('widgy.contrib.widgy_mezzanine.views',
    url('^(?P<node_pk>.*)/$', 'handle_form'),
)
