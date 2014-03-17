Changelog
=========

0.2.0
-----

* Use django-pyscss_ for SCSS compilation. Requires an update to the
  COMPRESS_PRECOMPILERS setting::

    COMPRESS_PRECOMPILERS = (
        ('text/x-scss', 'django_pyscss.compressor.DjangoScssFilter'),
    )

  You may also have to update ``@import`` statements in your SCSS, because
  django-pyscss uses a different (more consistent) rule for path resolution.
  For example, ``@import 'widgy_common'`` should be changed to ``@import
  '/widgy/css/widgy_common'``

.. _django-pyscss: https://github.com/fusionbox/django-pyscss

0.1.2 (2013-10-23)
------------------

* Fix Widgy admin for static files hosted on a different domain

0.1.1 (2013-10-21)
------------------

* Adjust ``MANIFEST.in`` to fix PyPi install.
* Fix layout having a unicode ``verbose_name``

0.1.0 (2013-10-18)
------------------

First release.

Basic features:

* Heterogeneous tree editor (``widgy``)
* CMS (``widgy.contrib.widgy_mezzanine``)
* CMS Plugins (``widgy.contrib.urlconf_include``)
* Widgets (``widgy.contrib.page_builder``)
* Form builder (``widgy.contrib.form_builder``)
* Multilingual pages (``widgy.contrib.widgy_i18n``)
* Review queue (``widgy.contrib.review_queue``)
