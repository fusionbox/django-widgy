Changelog
=========

0.8.4 (2016-06-03)
------------------

- Add atomic blocks around multi-step operations [#376]


0.8.3 (2016-04-29)
------------------

- Fix bug in cross domain requests in admin


0.8.2 (2016-04-15)
------------------

- Fixes issue #371


0.8.1 (2016-04-13)
------------------

- **Possible Breaking Change** Remove ``node-icon-sprite`` in
  ``widgy_common.scss`` this is incompatible with django storages.
- Add ``WidgySite.valid_root_of`` method. You can override this method to
  specify which layouts will be available for new pages.
- Django 1.9 support
- Improved translations
- Bugfixes


0.7.4 (2015-11-17)
------------------

- Fix compatibility with django-filer 1.0.2


0.7.3 (2015-09-17)
------------------

- Include and install DaisyDiff binaries and license files.


0.7.2 (2015-09-15)
------------------

- Include DaisyDiff.jar with distribution.


0.7.1 (2015-08-18)
------------------

- Fix python 3 compatibility: SortedDict.keys() was returning an iterator
  instead of a view. This was causing ``form_builder/forms/XX`` not to display
  properly.


0.7.0 (2015-07-31)
------------------

- **Possible Breaking Change** Updated the django-pyscss_ dependency. Please
  see the `django-pyscss changelog
  <https://pypi.python.org/pypi/django-pyscss/2.0.0#changelog>`_ for
  documentation on how/if you need to change anything.
- Django 1.8 compatibility.
- Python 3 compatibility
- Django 1.7 is now the minimum supported version
- Mezzanine 4.0 is now the minimum supported version
- ``Content.clone`` now copies simple many-to-many relationships. If you have a
  widget with a many-to-many field and an overridden clone method that calls
  super, you should take this into account. If you have many-to-many
  relationships that use a custom through table, you will have to continue to
  override clone to clone those.
- **Backwards Incompatible** ``WidgySite.has_add_permission`` signature
  changed.
- Multisite support

  * One widgy project can now respond to multiple domains. Use cases could be
    Widgy as a Service or multi-franchise website.
  * This feature depends on `Mezzanine multi-tenancy
    <http://mezzanine.jupo.org/docs/multi-tenancy.html>`_
  * Callouts are now tied to a django site
  * This feature is provided by
    ``widgy.contrib.widgy_mezzanine.site.MultiSitePermissionMixin``


0.6.1 (2015-05-01)
------------------

- Fix non-determinism bug with find_media_files.


0.6.0 (2015-04-30)
------------------

- Improved the compatibility error messages [#299, #193]
- Remove the recommendation to use mezzanine.boot as it was not required [#291]
- **Possible Breaking Change** Updated the django-pyscss_ dependency. Please
  see the `django-pyscss changelog
  <https://pypi.python.org/pypi/django-pyscss/2.0.0#changelog>`_ for
  documentation on how/if you need to change anything.
- By default, Widgy views are restricted to staff members. Previously any
  authenticated user was allowed. This effects the preview view and pop out
  edit view, among others. If you were relying on the ability for any user to
  access those, override ``authorize_view`` in your ``WidgySite``. [#267]::

    class MyWidgySite(WidgySite):
        def authorize_view(self, request, view):
            if not request.user.is_authenticated()
                raise PermissionDenied


0.5.0 (2015-04-17)
------------------

- **Backwards Incompatible** RichTextPage is no longer unregistered by default
  in widgy_mezzanine. If you wish to unregister it, you can add the following
  to your admin.py file::

      from django.contrib import admin
      from mezzanine.pages.models import RichTextPage
      admin.site.unregister(RichTextPage)

- Bugfix: Previously, the Widgy editor would break if CSRF_COOKIE_HTTPONLY was
  set to True [#311]

- Switched to py.test for testing. [#309]


0.4.0 (2015-03-12)
------------------

- Django 1.7 support. Requires upgrade to South 1.0 (Or use of
  SOUTH_MIGRATION_MODULES) if you stay on Django < 1.7. You may have to --fake
  some migrations to upgrade to the builtin Django migrations. Make sure your
  database is up to date using South, then upgrade Django and run::


  ./manage.py migrate --fake widgy
  ./manage.py migrate --fake easy_thumbnails
  ./manage.py migrate

- Support for installing Widgy without the dependencies of its contrib apps.
  The 'django-widgy' package only has dependencies required for Widgy core.
  Each contrib package has a setuptools 'extra'. To install everything, replace
  'django-widgy' with 'django-widgy[all]'. [#221]

- Switched to tox for test running and allow running core tests without
  contrib. [#294]

- Stopped relying on urls with consecutive '/' characters [#233]. This adds a new
  urlpattern for widgy_mezzanine's preview page and form submission handler.
  The old ones will keep working, but you should reverse with 'page_pk' instead
  of 'slug'. For example::

    url = urlresolvers.reverse('widgy.contrib.widgy_mezzanine.views.preview', kwargs={
        'node_pk': node.pk,
        'page_pk': page.pk,
    })

- Treat help_text for fields in a widget form as safe (HTML will not be
  escaped) [#298]. If you were relying on HTML special characters being
  escaped, you should replace ``help_text="1 is < 2"`` with
  ``help_text=django.utils.html.escape("1 is < 2")``.

- Reverse URLs in form_builder admin with consideration for Form
  subclasses [#274].


0.3.5 (2015-01-30)
------------------

Bugfix release:

- Set model at runtime for ClonePageView and UnpublishView [Rocky Meza, #286]

0.3.4 (2015-01-22)
------------------

Bugfix release:

- Documentation fixes [Rocky Meza and Gavin Wahl]
- Fixes unintentional horizontal scrolling of Widgy content [Justin Stollsteimer]
- Increased spacing after widget title paragraphs [Justin Stollsteimer]
- Fixed styles in ckeditor to show justifications [Zachery Metcalf, #279]
- Eliminated the margins for InvisibleMixin [Rocky Meza]
- CSS support for adding fields to Image. [Rocky Meza]
- Additional mezzanine container style overflow fixes [Justin Stollsteimer]
- Fix r.js optimization errors with daisydiff [Rocky Meza]
- Remove delete button from widgypage add form [Gavin Wahl]


0.3.3 (2014-12-22)
------------------
Bugfix release:

- Allow cloning with an overridden WIDGY_MEZZANINE_PAGE_MODEL [Zach Metcalf, #269]
- SCSS syntax error [Rivo Laks, #271]

0.3.2 (2014-10-16)
------------------

Bugfix release:

- Allow WidgyAdmin to check for ReviewedWidgySite without review_queue
  installed [Scott Clark, #265]
- Fix handling of related_name on ProxyGenericRelation [#264]


0.3.1 (2014-10-01)
------------------

Bugfix release for 0.3.0. #261, #263.

0.3.0 (2014-09-24)
------------------

This release mainly focusses on the New Save Flow feature, but also includes
several bug fixes and some nice CSS touch ups.  There have been some updates to
the dependencies, so please be sure to check the `How to Upgrade`_ section to
make sure that you get everything updated correctly.

Major Changes
^^^^^^^^^^^^^

* New Save Flow **Requires upgrading Mezzanine to at least 3.1.10** [Gavin
  Wahl, Rocky Meza, #241]

  We have updated the workflow for WidgyPage.  We consider this an experiment
  that we can hopefully expand to all WidgyAdmins in the future.  We hope that
  this new save flow is more intuitive and less tedious.

  Screenshot of before:

  .. image:: https://raw.githubusercontent.com/fusionbox/django-widgy/master/docs/_images/new-save-flow_before.png
     :alt: Widgy Page Admin Old Save Flow

  Screenshot of after:

  .. image:: https://raw.githubusercontent.com/fusionbox/django-widgy/master/docs/_images/new-save-flow_after.png
     :alt: Widgy Page Admin New Save Flow

  As you can see, we have rearranged some of the buttons and have gotten rid of
  the Published Status button.  The new save buttons on the bottom right now
  will control the publish state as well as the commit status.  This means that
  now instead of committing and saving being a two-step process, it all lives
  in one button.  This should make editing and saving a smoother process.
  Additionally, we have renamed some buttons to make their intent more obvious.

Bug Fixes
^^^^^^^^^

* Updated overridden directory_table template for django-filer 0.9.6. **Requires
  upgrading django-filer to at least 0.9.6**. [Scott Clark, #179]
* Fix bug in ReviewedVersionTrackerQuerySet.published [Gavin Wahl, #240]
* Made commit buttons not look disabled [Justin Stollsteimer, #250, #205]
* (Demo) Added ADD_PAGE_ORDER to demo settings [Zach Metcalf, #248]
* (Demo) Updated demo project requirements [Scott Clark, #234]
* Make Widgy's jQuery private to prevent clashes with other admin extensions [Gavin Wahl, #246]

Documentation
^^^^^^^^^^^^^

* Update recommend ADMIN_MENU_ORDER to clarify django-filer [Gavin Wahl, #249]

How to Upgrade
^^^^^^^^^^^^^^

In this release, widgy has udpated two of its dependencies:

* The minimum supported version of django-filer is now 0.9.6 (previously 0.9.5).
* The minimum supported version of Mezzanine is now 3.1.10 (previously 1.3.0).

If you ``pip install django-widgy==0.3.0``, it should upgrade the dependencies
for you, but just to be sure, you may want to also run ::

    pip install 'django-filer>=0.9.6' 'Mezzanine>=3.1.10'

to make sure that you get the updates.

.. note::

    Please note that if you are upgrading from an older version of Mezzanine,
    that the admin center has been restyled a little bit.


0.2.0 (2014-08-04)
------------------

Changes
^^^^^^^

* Widgy is now Apache Licensed
* **Breaking Change** Use django-pyscss_ for SCSS compilation. [Rocky Meza, #175]

  Requires an update to the ``COMPRESS_PRECOMPILERS`` setting::

    COMPRESS_PRECOMPILERS = (
        ('text/x-scss', 'django_pyscss.compressor.DjangoScssFilter'),
    )

  You may also have to update ``@import`` statements in your SCSS, because
  django-pyscss uses a different (more consistent) rule for path resolution.
  For example, ``@import 'widgy_common'`` should be changed to ``@import
  '/widgy/css/widgy_common'``
* Added help_text to Section to help user avoid bug [Zach Metcalf, #135]
* Allow UI to updated based on new data after reposition [Gavin Wahl, #199]
* Changed Button's css_classes in shelf [Rocky Meza, #203]
* Added loading cursor while ajax is in flight [Gavin Wahl, #215, #208]
* Get rid of "no content" [Gavin Wahl, #206]
* Use sprites for the widget icons [Gavin Wahl and Rocky Meza, #89, #227]
* Only show approve/unapprove buttons for interesting commits [Gavin Wahl, #228]
* Updated demo app to have new design and new widgets [Justin Stollsteimer, Gavin Wahl, Antoine Catton and Rocky Meza, #129, #176]
* Added cloning for WidgyPages [Gavin Wahl, #235]
* Use a more realistic context to render pages for search [Gavin Wahl, #166]
* Add default children to Accordion and Tabs [Rocky Meza, #238]

Bugfixes
^^^^^^^^

* Fix cursors related to dragging [Gavin Wahl, #155]
* Update safe urls [Gavin Wahl, #212]
* Fix widgy_mezzanine preview for Mezzanine==3.1.2 [Rocky Meza, #201]
* Allow RichTextPage in the admin [Zach Metcalf, #197]
* Don't assume the response has a content-type header [Gavin Wahl, #216]
* Fix bug with FileUpload having empty values [Rocky Meza, #217]
* Fix urlconf_include login_required handling [Gavin Wahl, #200]
* Patch fancybox to work with jQuery 1.9 [Gavin Wahl, #222]
* Fix some import errors in SCSS [Rocky Meza, #230]
* Fix restore page in newer versions of Mezzanine [Gavin Wahl, #232]
* Use unicode format strings in review queue [Gavin Wahl, #236]

Documentation
^^^^^^^^^^^^^

* Updated quickstart to cover south migrations with easy_thumbnails [Zach Metcalf, #202]
* Added Proxy Widgy Model Tutorial [Zach Metcalf, #210]

.. _django-pyscss: https://github.com/fusionbox/django-pyscss

0.1.6 (2014-09-09)
------------------
* Fix migrations containing unsupported KeywordsField from mezzanine [Scott Clark]
* Rename package to django-widgy


0.1.5 (2013-11-23)
------------------

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
