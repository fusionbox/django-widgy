from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from widgy import registry
from widgy.db.fields import WidgyField
from widgy.contrib.page_builder.models import Layout, MainContent, Accordion


class TwoContentLayout(Layout):
    default_children = [
        (MainContent, (), {}),
        (MainContent, (), {}),
    ]

    class Meta:
        verbose_name = 'Two Content Layout'

registry.register(TwoContentLayout)


class DemoAccordion(Accordion):
    class Meta:
        proxy = True
        verbose_name = 'Accordion'

    def valid_parent_of(self, cls, obj=None):
        if obj and obj in self.get_children():
            return True
        else:
            sup = super(DemoAccordion, self).valid_parent_of(cls)
            if isinstance(self.get_root(), TwoContentLayout):
                return sup and len(self.get_children()) < 2
            else:
                return sup

registry.unregister(Accordion)
registry.register(DemoAccordion)


class I18NThing(models.Model):
    name = models.CharField(_('name'), max_length=255)

    description = WidgyField(
        site=settings.WIDGY_MEZZANINE_SITE,
        verbose_name=_('description'),
        root_choices=(
            'widgy_i18n.I18NLayoutContainer',
        ))

    class Meta:
        verbose_name = _('event')
        verbose_name_plural = _('events')
