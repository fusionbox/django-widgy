Building Widgy's JavaScript With RequireJS
==========================================

Widgy's editing interface uses RequireJS to handle dependency management
and to encourage code modularity. This is convenient for development,
but might be slow in production due to the many small JavaScript files.
Widgy supports building its JavaScript with the `RequireJS optimizer`_
to remedy this. This is entirely optional and only necessary if the
performance of loading many small JavaScript and template files bothers
you.

To build the JavaScript,

  - Install ``django-require``::

      pip install django-require

  - Add the settings for django-require::

      REQUIRE_BUILD_PROFILE = 'widgy.build.js'
      REQUIRE_BASE_URL = 'widgy/js'
      STATICFILES_STORAGE = 'require.storage.OptimizedStaticFilesStorage'

  - Install ``node`` or ``rhino`` to run ``r.js``. django-require will
    detect which one you installed. ``rhino`` is nice because you can
    apt-get it::

      apt-get install rhino

Now the JavaScript will automatically built during
:django:djadmin:`collectstatic`.


.. _RequireJS optimizer: http://requirejs.org/docs/optimization.html
