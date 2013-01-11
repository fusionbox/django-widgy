from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from mezzanine.pages.models import Page

from widgy.db.fields import WidgyField


class WidgyPage(Page):
    root_node = WidgyField(
        site=settings.WIDGY_MEZZANINE_SITE,
        verbose_name=_('widgy content'),
        root_choices=(
            'page_builder.Layout',
        ))

    class Meta:
        verbose_name = _('widgy page')
        verbose_name_plural = _('widgy pages')
