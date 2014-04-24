Widgy I18N
==========

.. currentmodule:: widgy.contrib.widgy_i18n.models

This app provides helpers for working with internationalization and
localization on widgy trees.  widgy_i18n provides two important mixins,
:class:`I18NChild` and :class:`I18NTabbedContainer`.  A
:class:`I18NTabbedContainer` is a container for many :class:`I18NChild` objects
and it decides which to render based on the current language.  The only thing
that :class:`I18NChild` does is store the language code for what language it
is.

widgy_i18n also provides a class, :class:`I18NLayoutContainer` which works at
the root level to decide which layout class to render based on the current
language.  It is intended to be proxied and has a required attribute named
``child_class``.  ``child_class`` refers to the specific :class:`I18NChild`
that this container accepts.


If for example, you had a ``HomeLayout`` class that you wanted to be
internationalized, you would do something like this::

    import widgy
    from widgy.contrib.page_builder.models import Layout
    from widgy.contrib.widgy_i18n.models import I18NChild, I18NLayoutContainer


    @widgy.register
    class HomeLayout(I18NChild, Layout):
        # Make sure HomeLayout inherits from I18NChild

        @classmethod
        def valid_child_of(cls, parent, obj=None):
            # we only want HomeLayouts to go inside HomeLayoutContainers
            return isinstance(parent, HomeLayoutContainer)

    @widgy.register
    class HomeLayoutContainer(I18NLayoutContainer):
        # Tell I18NLayoutContainer which Layout class to use.
        child_class = HomeLayout

        class Meta:
            # make it a proxy model so that you don't need to add another
            # table
            proxy = True

Then you have to change your :class:`~widgy.db.fields.WidgyField` declaration
to include your new ``HomeLayoutContainer`` in the ``root_choices``.  Below is
an example for if you are using :doc:`../widgy-mezzanine/index`. It overrides
the :class:`~widgy.db.fields.VersionedWidgyField` in order to point the
``root_choices`` parameter to the ``HomeLayoutContainer``.  Also, it provides a
preview link for each language so that the admin user can preview each page no
matter what language they are viewing the admin center in.::

    from django.db import models
    from django.utils.translation import ugettext_lazy as _, activate, get_language
    from django.conf import settings
    from django.core import urlresolvers

    from mezzanine.pages.models import Page

    from widgy.db.fields import VersionedWidgyField
    from widgy.models import links
    from widgy.contrib.widgy_mezzanine.models import WidgyPageMixin

    def i18nreverse(language, *args, **kwargs):
        current_language = get_language()
        activate(language)
        url = urlresolvers.reverse(*args, **kwargs)
        activate(current_language)
        return url

    @links.register
    class WidgyPage(WidgyPageMixin, Page):
        root_node = VersionedWidgyField(
            site=settings.WIDGY_MEZZANINE_SITE,
            to=getattr(settings, 'WIDGY_MEZZANINE_VERSIONTRACKER', None),
            verbose_name=_('widgy content'),
            root_choices=(
                'yourapp.HomeLayoutContainer',
            ))

        # If you are using something like django-modeltranslation for
        # translating the title and metadata of the page (aka the data that
        # doesn't live in the widgy tree), Mezzanine's built-in KeywordsField
        # is incompatible and you would need this extra field.
        seo_keywords = models.TextField(_('keywords'), blank=True)

        class Meta:
            verbose_name = _('widgy page')
            verbose_name_plural = _('widgy pages')

        def get_action_links(self, root_node):
            # Provide the preview links for the various languages.
            return [
                {
                    'type': 'preview',
                    'text': _('Preview (%s)') % node.content.language_code,
                    'url': i18nreverse(node.content.language_code,
                        'widgy.contrib.widgy_mezzanine.views.preview',
                        kwargs={'slug': self.slug, 'node_pk': node.pk}
                    )
                }
                for node in root_node.get_children()
            ]

To use this new ``WidgyPage`` class, you just have to change the
:setting:`WIDGY_MEZZANINE_PAGE_MODEL` setting to point to your ``WidgyPage``
definition.  In this example it would point to ``yourapp.WidgyPage``.
