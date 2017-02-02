from django.conf.urls import url, include

from .widgy_config import widgy_site

urlpatterns = [
    url('', include(widgy_site.urls)),
]
