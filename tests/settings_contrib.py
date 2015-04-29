from settings import *


PACKAGE_NAME_FILEBROWSER = "filebrowser_safe"
PACKAGE_NAME_GRAPPELLI = "grappelli_safe"
GRAPPELLI_INSTALLED = True

INSTALLED_APPS += [
    'mezzanine.conf',
    'mezzanine.core',
    'mezzanine.generic',
    'mezzanine.pages',
    'mezzanine.forms',
    'django.contrib.comments',
    'filebrowser_safe',
    'grappelli_safe',
    'filer',
    'widgy.contrib.widgy_mezzanine',
    'widgy.contrib.form_builder',
    'widgy.contrib.page_builder',
    'widgy.contrib.urlconf_include',
    'widgy.contrib.widgy_i18n',
]


TEMPLATE_CONTEXT_PROCESSORS += (
    "mezzanine.conf.context_processors.settings",
    "mezzanine.pages.context_processors.page",
)
