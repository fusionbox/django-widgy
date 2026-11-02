from django.urls import include, re_path
from django.conf import settings
from django.contrib import admin


def dummy_view(*args, **kwargs):
    pass


urlpatterns = [
    re_path('^core_tests/', include('tests.core_tests.urls')),
    re_path("^admin/", admin.site.urls),
    # mezzanine.pages.views.page reverses the 'home' url.
    re_path('^$', dummy_view, name='home'),
]

if 'widgy.contrib.widgy_mezzanine' in settings.INSTALLED_APPS:
    urlpatterns += [
        re_path('^widgy-mezzanine/', include('widgy.contrib.widgy_mezzanine.urls')),
        re_path('^mezzanine/', include('mezzanine.urls')),
    ]
