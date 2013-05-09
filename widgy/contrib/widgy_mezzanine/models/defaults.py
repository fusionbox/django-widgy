from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from mezzanine.pages.models import Page

from widgy.db.fields import VersionedWidgyField
from widgy.contrib.widgy_mezzanine.mixins import WidgyPageMixin


class WidgyPage(WidgyPageMixin, Page):
    root_node = VersionedWidgyField(
        site=settings.WIDGY_MEZZANINE_SITE,
        to=getattr(settings, 'WIDGY_MEZZANINE_VERSIONTRACKER', None),
        verbose_name=_('widgy content'),
        root_choices=(
            'page_builder.Layout',
        ))

    class Meta:
        app_label = 'widgy_mezzanine'
        verbose_name = _('widgy page')
        verbose_name_plural = _('widgy pages')
