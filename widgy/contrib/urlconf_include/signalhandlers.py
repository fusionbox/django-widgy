from importlib import import_module

from django.core.urlresolvers import set_urlconf
from django.dispatch import receiver
from django.conf import settings

from widgy.signals import widgy_pre_index



@receiver(widgy_pre_index)
def patch_url_conf(sender, **kwargs):
    from .middleware import PatchUrlconfMiddleware
    root_urlconf = import_module(settings.ROOT_URLCONF)
    urlconf = PatchUrlconfMiddleware.get_urlconf(root_urlconf)
    set_urlconf(urlconf)
