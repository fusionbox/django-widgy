from django.core.urlresolvers import set_urlconf
from django.dispatch import receiver
from django.conf import settings
from django.utils.importlib import import_module

from widgy.contrib.widgy_mezzanine.signals import widgypage_pre_index



@receiver(widgypage_pre_index)
def patch_url_conf(sender, **kwargs):
    from .middleware import PatchUrlconfMiddleware
    root_urlconf = import_module(settings.ROOT_URLCONF)
    urlconf = PatchUrlconfMiddleware.get_urlconf(root_urlconf)
    set_urlconf(urlconf)
