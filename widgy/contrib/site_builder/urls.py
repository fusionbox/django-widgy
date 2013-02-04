from django.conf.urls.defaults import patterns, url


# Page patterns.
urlpatterns = patterns('widgy.contrib.site_builder.views',
    url("^(?P<slug>.*)/$", 'page_detail'),
)
