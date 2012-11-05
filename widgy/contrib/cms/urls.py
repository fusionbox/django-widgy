from django.conf.urls import patterns, url

urlpatterns = patterns(
    'widgy.contrib.cms.views',
    url(r'^common-callouts/', 'callout_browse')
)
