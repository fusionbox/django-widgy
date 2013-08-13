from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.core import urlresolvers

from mezzanine.pages.managers import PageManager
from mezzanine.pages.models import Link

from widgy.utils import SelectRelatedManager
from widgy.models import links


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
        return ', '.join(unicode(keyword) for keyword in self.keywords.all())

    def get_form_action_url(self, form, widgy):
        return urlresolvers.reverse(
            'widgy.contrib.widgy_mezzanine.views.handle_form',
            kwargs={
                'form_node_pk': form.node.pk,
                'slug': self.slug,
            })

    def get_action_links(self, root_node):
        return [
            {
                'type': 'preview',
                'text': _('Preview'),
                'url': urlresolvers.reverse(
                    'widgy.contrib.widgy_mezzanine.views.preview',
                    kwargs={'slug': self.slug, 'node_pk': root_node.pk}
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


class PageSelectRelatedManager(SelectRelatedManager, PageManager):
    """
    WidgyPage's manager must be a PageManager.
    """
    use_for_related_fields = True

links.register(Link)

# In Django 1.5+, we could use swappable = True
if getattr(settings, 'WIDGY_MEZZANINE_PAGE_MODEL', None) is None:
    from mezzanine.pages.models import Page
    from widgy.db.fields import VersionedWidgyField

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

        objects = PageSelectRelatedManager(select_related=[
            'root_node'
            'root_node__head',
            # we might not need this, if head isn't published, but we
            # probably will.
            'root_node__head__root_node',
        ])
