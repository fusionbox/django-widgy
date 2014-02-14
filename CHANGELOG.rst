Changelog
=========

0.1.6 (Not released yet)
------------------------
* Fix migrations containing unsupported KeywordsField from mezzanine [Scott Clark]


0.1.5 (2013-11-23)
------------------------

* Fix Widgy migrations without Mezzanine [Gavin Wahl]
* Drop target collision detection [Gavin Wahl]
* Fix Figure and StrDisplayNameMixin [Gavin Wahl]
* Avoid loading review_queue when it's not installed [Scott Clark]
* Fix multi-table inheritance with LinkFields [Gavin Wahl]

0.1.4 (2013-11-04)
------------------

* Add StrDisplayNameMixin

0.1.3 (2013-10-25)
------------------

* Fix image widget validation with the S3 storage backend

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
