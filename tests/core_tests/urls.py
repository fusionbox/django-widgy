from django.urls import include, path

from .widgy_config import widgy_site

urlpatterns = [
    path('', include(widgy_site.urls)),
]
