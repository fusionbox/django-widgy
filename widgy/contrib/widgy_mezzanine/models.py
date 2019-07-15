from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_text
from django.conf import settings
from django.core import urlresolvers
from django.db.models.signals import post_migrate
from django.db import transaction

from mezzanine.pages.managers import PageManager
from mezzanine.pages.models import Link, Page
from mezzanine.utils.sites import current_site_id

from widgy.db.fields import VersionedWidgyField
from widgy.utils import SelectRelatedManager
from widgy.models import links
from widgy.contrib.page_builder.models import CalloutWidget, Callout
import widgy


class WidgyPageMixin(object):
    base_template = 'widgy/mezzanine_base.html'

    @property
    def seo_keywords(self):
        """
        This is here to prevent a mess in the template, but also because the
        KeywordsField from mezzanine seems to be doing much too much for what
        we need.  We also override this with a real db column in order to do
        translation.
        """
        return ', '.join(force_text(keyword) for keyword in self.keywords.all())

    def get_form_action_url(self, form, widgy):
        return urlresolvers.reverse(
            'widgy.contrib.widgy_mezzanine.views.handle_form',
            kwargs={
                'form_node_pk': form.node.pk,
                'slug': self.pk,
            })

    def get_action_links(self, root_node):
        return [
            {
                'type': 'preview',
                'text': _('Preview'),
                'url': urlresolvers.reverse(
                    'widgy.contrib.widgy_mezzanine.views.preview',
                    kwargs={'page_pk': self.pk, 'node_pk': root_node.pk}
                )
            },
        ]

    def get_content_model(self):
        """
        This is needed to render an unsaved WidgyPage. The template
        calls get_content_model, which should work because we inherit it
        from Page. However, the default implementation does a database
        query, which of course can't find anything because we are trying
        to render an unsaved object. This functionality is used on the
        fake WidgyPage used to preview while undeleting.
        """
        return self


class UseForRelatedFieldsSelectRelatedManager(SelectRelatedManager):
    """
    We use this to optimize page rendering. This is the manager that will be
    used to select the WidgyPage when mezzanine does `page.widgypage`.
    """
    use_for_related_fields = True


widgy.unregister(CalloutWidget)


@widgy.register
class MezzanineCalloutWidget(CalloutWidget):
    class Meta:
        verbose_name = _('callout widget')
        verbose_name_plural = _('callout widgets')
        proxy = True

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'callout':
            cond = models.Q(site=None) | models.Q(site=current_site_id())
            kwargs['queryset'] = Callout.objects.filter(cond)
        return super(CalloutWidget, self).formfield_for_dbfield(db_field, **kwargs)


@links.register
class WidgyPage(WidgyPageMixin, Page):
    root_node = VersionedWidgyField(
        site=settings.WIDGY_MEZZANINE_SITE,
        verbose_name=_('widgy content'),
        root_choices=(
            'page_builder.Layout',
        ),
        # WidgyField used to have these as defaults.
        null=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        verbose_name = _('widgy page')
        verbose_name_plural = _('widgy pages')
        swappable = 'WIDGY_MEZZANINE_PAGE_MODEL'

    select_related_manager = UseForRelatedFieldsSelectRelatedManager(select_related=[
        'root_node',
        'root_node__head',
        # we might not need this, if head isn't published, but we
        # probably will.
        'root_node__head__root_node',
    ])
    base_manager_name = 'select_related_manager'
    objects = PageManager()


links.register(Link)


class PathRoot(models.Transform):
    lookup_name = 'path_root'

    @property
    def steplen(self):
        """
        Length of a step for the materialized tree
        """
        return self.lhs.output_field.model.steplen

    def as_sql(self, qn, connection):
        lhs, params = qn.compile(self.lhs)
        return 'SUBSTR(%s, %%s, %%s)' % lhs, (params + [1, self.steplen])

models.Field.register_lookup(PathRoot)
