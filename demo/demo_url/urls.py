from django.conf.urls import patterns, include, url
from django.views.generic import RedirectView

from . import views

urlpatterns = patterns('',
    (r'^$', RedirectView.as_view(url='hello/')),
    (r'^hello/', views.hello),
)
