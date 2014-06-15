Widgy Mezzanine
===============

This app provides integration with the Mezzanine_ project. Widgy Mezzanine uses
Mezzanine for site structure and Widgy for page content. It does this by
providing a subclass of Mezzanine's Page model called
:class:`~widgy.contrib.widgy_mezzanine.models.WidgyPage` which delegates to
Page Builder for all content.

The dependencies for Widgy Mezzanine (Mezzanine and Widgy's Page Builder app)
are not installed by default when you install widgy, you can install them
yourself::

    $ pip install Mezzanine django-widgy[page_builder]

or you can install them using through the widgy package::

    $ pip install django-widgy[page_builder,widgy_mezzanine]

In order to use Widgy Mezzanine, you must provide ``WIDGY_MEZZANINE_SITE`` in
your settings.  This is a fully-qualified import path to an instance of
:class:`~widgy.site.WidgySite`.  You also need to install the URLs. ::

    url(r'^widgy-mezzanine/', include('widgy.contrib.widgy_mezzanine.urls')),


.. class:: widgy.contrib.widgy_mezzanine.models.WidgyPage

    The :class:`~widgy.content.widgy_mezzanine.models.WidgyPage` class is
    ``swappable`` like :class:`~django.contrib.auth.models.User`.  If you want to
    override it, specify a ``WIDGY_MEZZANINE_PAGE_MODEL`` in your settings.  the
    :class:`widgy.contrib.widgy_mezzanine.models.WidgyPageMixin` mixin is
    provided for ease of overriding.  Any code that references a
    :class:`~widgy.contrib.widgy_mezzanine.models.WidgyPage` should use the
    :func:`widgy.contrib.widgy_mezzanine.get_widgypage_model` to get the
    correct class.


.. _Mezzanine: http://mezzanine.jupo.org/
