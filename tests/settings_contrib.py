from .settings import *


PACKAGE_NAME_FILEBROWSER = "filebrowser_safe"
PACKAGE_NAME_GRAPPELLI = "grappelli_safe"
GRAPPELLI_INSTALLED = True

INSTALLED_APPS += [
    'django.contrib.redirects',
    'mezzanine.conf',
    'mezzanine.core',
    'mezzanine.generic',
    'mezzanine.pages',
    'mezzanine.forms',
    'filebrowser_safe',
    'grappelli_safe',
    'filer',
    'easy_thumbnails',
    'widgy.contrib.widgy_mezzanine',
    'widgy.contrib.form_builder',
    'widgy.contrib.page_builder',
    'widgy.contrib.urlconf_include',
    'widgy.contrib.widgy_i18n',
]

# XXX Mezzanine insists on having some version of django comments installed.
try:
    import django_comments
except ImportError:
    INSTALLED_APPS.append('django.contrib.comments')
else:
    INSTALLED_APPS.append('django_comments')



TEMPLATE_CONTEXT_PROCESSORS += (
    "mezzanine.conf.context_processors.settings",
    "mezzanine.pages.context_processors.page",
)
