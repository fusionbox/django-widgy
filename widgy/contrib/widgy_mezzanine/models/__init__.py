from django.conf import settings

from widgy.utils import fancy_import


WIDGY_PAGE_MODEL = getattr(settings, 'WIDGY_MEZZANINE_PAGE_MODEL', 'widgy.contrib.widgy_mezzanine.models.defaults.WidgyPage')

WidgyPage = fancy_import(WIDGY_PAGE_MODEL)
