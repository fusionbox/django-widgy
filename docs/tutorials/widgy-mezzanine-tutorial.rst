Quickstart
==========

This quickstart assumes you wish to use the following packages:

-  Widgy Mezzanine
-  Page Builder
-  Form Builder


Install the Widgy package::

    cd widgy
    pip install -e .

Add Mezzanine apps to ``INSTALLED_APPS``::

        'mezzanine.boot',
        'mezzanine.conf',
        'mezzanine.core',
        'mezzanine.generic',
        'mezzanine.pages',
        'django.contrib.comments',
        'django.contrib.sites',
        'filebrowser_safe',
        'grappelli_safe',

add Widgy to ``INSTALLED_APPS``::

        'widgy',
        'widgy.contrib.page_builder',
        'widgy.contrib.form_builder',
        'widgy.contrib.widgy_mezzanine',

add required Widgy apps to ``INSTALLED_APPS``::

        'filer',
        'easy_thumbnails',
        'compressor',
        'argonauts',
        'scss',
        'sorl.thumbnail',
        'south',


``django.contrib.admin`` should be installed after Mezzanine and Widgy,
so move it under them in ``INSTALLED_APPS``.

add Mezzanine middleware::

        'mezzanine.core.request.CurrentRequestMiddleware',
        'mezzanine.core.middleware.AdminLoginInterfaceSelectorMiddleware',
        'mezzanine.pages.middleware.PageMiddleware',

Mezzanine settings::

    PACKAGE_NAME_FILEBROWSER = "filebrowser_safe"
    PACKAGE_NAME_GRAPPELLI = "grappelli_safe"
    ADMIN_MEDIA_PREFIX = STATIC_URL + "grappelli/"
    TESTING = False
    GRAPPELLI_INSTALLED = True
    SITE_ID = 1

If you want mezzanine to use
:class:`~widgy.contrib.widgy_mezzanine.models.WidgyPage` as the default page,
you can add the following line to your settings file::

    ADD_PAGE_ORDER = (
        'widgy_mezzanine.WidgyPage',
    )

add Mezzanine context processor. If you don't already have
``TEMPLATE_CONTEXT_PROCESSORS`` in your settings file, you should copy the
default before add Mezzanine's::

    TEMPLATE_CONTEXT_PROCESSORS = (
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
        "django.core.context_processors.debug",
        "django.core.context_processors.i18n",
        "django.core.context_processors.static",
        "django.core.context_processors.media",
        "django.core.context_processors.request",
        "mezzanine.conf.context_processors.settings",
    )

make a :class:`Widgy site <widgy.site.WidgySite>` and set it in settings::

    # demo/widgy_site.py
    from widgy.site import WidgySite

    class WidgySite(WidgySite):
        pass

    site = WidgySite()

    # settings.py
    WIDGY_MEZZANINE_SITE = 'demo.widgy_site.site'

Configure django-compressor::

    STATICFILES_FINDERS = (
        'compressor.finders.CompressorFinder',
        'django.contrib.staticfiles.finders.FileSystemFinder',
        'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    )
    COMPRESS_ENABLED = True

add Widgy scss includes::

    import imp
    WIDGY_ROOT = imp.find_module('widgy')[1]
    SCSS_IMPORTS = (
        os.path.join(WIDGY_ROOT, 'static', 'widgy', 'css'),
    )

**Note:** Please put this before you define the ``COMPRESS_PRECOMPILERS``::

    COMPRESS_PRECOMPILERS = (
        ('text/x-scss', 'python -mscss.tool -C %s' %
         ' '.join(['-I "%s"' % d for d in SCSS_IMPORTS])
         ),
    )

Widgy requires that django-compressor be configured with a precompiler
for ``text/x-scss``.

syncdb; migrate

add urls::

    from django.conf.urls import patterns, include, url
    from demo.widgy_site import site as widgy_site

    urlpatterns = patterns('',
        # ...
        # widgy admin
        url(r'^admin/widgy/', include(widgy_site.urls)),
        # widgy frontend
        url(r'^widgy/', include('widgy.contrib.widgy_mezzanine.urls')),
        url(r'^', include('mezzanine.urls')),
    )


Make sure you have a url pattern named ``home`` or the admin templates
will not work right.

If you are using ``GenericTemplateFinderMiddleware``, use the one from
``fusionbox.mezzanine.middleware``. It has been patched to
work with Mezzanine.

How to edit home page
---------------------

1. Add the homepage to your urls.py::

       url(r'^$', 'mezzanine.pages.views.page', {'slug': '/'}, name='home'),

   **Note:** it must be a named URL, with the name 'home'

2. Make a page with the slug ``/`` and publish it.

3. Make a template called ``pages/index.html`` and put::

       {% extends "pages/widgypage.html" %}

   **Note:** If you don't do this you will likely get the following
   error::

       AttributeError: 'Settings' object has no attribute 'FORMS_EXTRA_FIELDS'

   This is caused by Mezzanine falling back its own template
   ``pages/index.html`` which tries to provide the inline editing feature,
   which requires ``mezzanine.forms`` to be installed.

Admin center
------------

A nice ``ADMIN_MENU_ORDER``::

    ADMIN_MENU_ORDER = [
        ('Widgy', (
            'pages.Page',
            'page_builder.Callout',
            'form_builder.Form',
            ('Review queue', 'review_queue.ReviewedVersionCommit'),
        )),
    ]

urlconf include
---------------

``urlconf_include`` is an optional application that allows you to install
urlpatterns in the Mezzanine page tree. To use it, put it in
``INSTALLED_APPS``,::

        'widgy.contrib.urlconf_include',

then add ``urlconf_include`` middleware,::

        'widgy.contrib.urlconf_include.middleware.PatchUrlconfMiddleware',

then set ``URLCONF_INCLUDE_CHOICES`` to a list of allowed urlpatterns. For example::

    URLCONF_INCLUDE_CHOICES = (
        ('blog.urls', 'Blog'),
    )
