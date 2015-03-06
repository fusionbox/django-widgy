Replacing CKEditor with Widgy
==============================

One use of Widgy is as a replacement to CKEditor. Suppose you have
something like this::

    class Post(models.Model):
        title = models.CharField()
        content = CKEDitorField()

And a template like this:

.. code-block:: html+django

    <h1>{{ post.title }}</h1>
    {{ post.content|safe }}

With Widgy, we'll be able to replace those with::

    from widgy.db.fields import WidgyField
    class Post(models.Model):
        title = models.CharField()
        content = WidgyField(
        root_choices=['page_builder.MainContent'],
        site='foo.site.widgy_site',
    )

And the new template:

.. code-block:: html+django

    {% load widgy_tags %}
    <h1>{{ post.title }}</h1>
    {% render_root post 'content' %}

And now we'll be able to use Widgy to edit Posts' content.

Installation
------------

Install Widgy and page_builder, the Widgy page content builder:

.. code-block:: html+django

    pip install django-widgy[page_builder]

Add Widgy and its dependencies to installed apps::

    'filer',
    'compressor',
    'argonauts',
    'easy_thumbnails',
    'sorl.thumbnail'
    'widgy',
    # not required, but this is where all the existing content widgets are
    'widgy.contrib.page_builder',

Make yourself a Widgy site. This controls Widgy configuration. The
defaults are fine for now. In foo/site.py::

    from widgy.site import WidgySite

    widgy_site = WidgySite()

And tell Widgy to use it in your settings::

    WIDGY_MEZZANINE_SITE = 'foo.site.widgy_site'

This shouldn't be required for much longer, it's an open issue to remove
this because we're not using Mezzanine right now. There is a small piece
of code in page_builder that still depends on this setting though.

Add Widgy urls::


    from foo.site import widgy_site
    urlpatterns = patterns('',
        # ...
        url(r'^admin/widgy/', include(widgy_site.urls)),
        # ...
    )

Configure django-compressor::

    STATICFILES_FINDERS = (
        'compressor.finders.CompressorFinder',
        'django.contrib.staticfiles.finders.FileSystemFinder',
        'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    )

    COMPRESS_PRECOMPILERS = (
        ('text/x-scss', 'django_pyscss.compressor.DjangoScssFilter'),
    )

    # if this hasn't been set already:
    STATIC_ROOT = os.path.join(BASE_DIR, 'foo/static')


The admin class for Post should inherit from WidgyAdmin. Here's an example of a
complete admin.py::

    from django.contrib import admin
    from widgy.admin import WidgyAdmin

    from foo.models import Post

    class PostAdmin(WidgyAdmin):
        pass

    admin.site.register(Post, PostAdmin)
