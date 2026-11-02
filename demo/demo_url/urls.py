from django.urls import re_path
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    re_path(r'^$', RedirectView.as_view(url='hello/')),
    re_path(r'^hello/', views.hello),
]
