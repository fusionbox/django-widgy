Writing Your First Widget
=========================

In this tutorial, we will build a Slideshow widget. You probably want to read
the :doc:`widgy-mezzanine-tutorial` to get a Widgy site running before you do
this one.

We currently have a static slideshow that we need to make editable. Users need
to be able to add any number of slides. Users also want to be able to change
the delay between each slide.

Here is the current slideshow HTML that is using `jQuery Cycle2`_:

.. code-block:: html+django

    <div class="cycle-slideshow"
         data-cycle-timeout="2000"
         data-cycle-caption-template="{% templatetag openvariable %}alt{% templatetag closevariable %}">
      <div class="cycle-caption"></div>

      <img src="http://placekitten.com/800/300" alt="Cute cat">
      <img src="http://placekitten.com/800/300" alt="Fuzzy kitty">
      <img src="http://placekitten.com/800/300" alt="Another cute cat">
      <img src="http://placekitten.com/800/300" alt="Awwww">
    </div>

.. seealso::

    :django:ttag:`templatetag`
         This template tag allows inserting the ``{{`` and ``}}`` characters
         needed by Cycle2.

.. _jQuery Cycle2: http://jquery.malsup.com/cycle2/

1.  Write the Models
--------------------

The first step in writing a widget is to write the models. We are going to
make a new Django app for these widgets.

.. code-block:: sh

    $ python manage.py startapp slideshow


(Don't forget to add ``slideshow`` to your :django:setting:`INSTALLED_APPS`).


Now let's write the models. We need to make a ``Slideshow`` model as the
container and a ``Slide`` model that represents the individual images. ::

    # slideshow/models.py
    from django.db import models
    import widgy
    from widgy.models import Content

    @widgy.register
    class Slideshow(Content):
        delay = models.PositiveIntegerField(default=2,
            help_text="The delay in seconds between slides.")

        accepting_children = True
        editable = True

    @widgy.register
    class Slide(Content):
        image = models.ImageField(upload_to='slides/', null=True)
        caption = models.CharField(max_length=255)

        editable = True

All widget classes inherit from :class:`widgy.models.base.Content`. This
creates the relationship with :class:`widgy.models.base.Node` and ensures that
all of the required methods are implemented.

In order to make a widget visible to Widgy, you have to add it to the registry.
There are two functions in the :mod:`widgy` module that help with this,
:func:`widgy.register` and :func:`widgy.unregister`. You should use the
:func:`widgy.register` class decorator on any model class that you wish to use
as a widget.

Both widgets need to have :attr:`~widgy.models.base.Content.editable` set to
``True``.  This will make an edit button appear in the editor, allowing the
user to set the ``image``, ``caption``, and ``delay`` values.

``Slideshow`` has :attr:`~widgy.models.base.Content.accepting_children` set to
``True`` so that you can put a ``Slide`` in it.  The default implementation of
:meth:`~widgy.models.base.Content.valid_parent_of` checks
:attr:`~widgy.models.base.Content.accepting_children`. We only need this until
we override :meth:`~widgy.models.base.Content.valid_parent_of` in :ref:`Step 3
<slideshow-compatibility>`.

.. note::

    As you can see, the ``image`` field is ``null=True``. It is necessary for
    all fields in a widget either to be ``null=True`` or to provide a default.
    This is because when a widget is dragged onto a tree, it needs to be saved
    without data.

    :class:`CharFields <django:django.db.models.CharField>` don't need to be
    ``null=True`` because if they are non-NULL, the default is an empty string.
    For most other field types, you must have ``null=True`` or a default value.

Now we need to generate migration for this app.

.. code-block:: sh

    $ python manage.py schemamigration --initial slideshow

And now run the migration.

.. code-block:: sh

    $ python manage.py migrate

2.  Write the Templates
-----------------------

After that, we need to write our templates. The templates are
expected to be named ``widgy/slideshow/slideshow/render.html`` and
``widgy/slideshow/slide/render.html``.

To create the slideshow template, add a file at
:file:`slideshow/templates/widgy/slideshow/slideshow/render.html`.

.. code-block:: html+django

    {% load widgy_tags %}
    <div class="cycle-slideshow"
      data-cycle-timeout="{{ self.get_delay_milliseconds }}"
      data-cycle-caption-template="{% templatetag openvariable %}alt{% templatetag closevariable %}">
      <div class="cycle-caption"></div>

      {% for child in self.get_children %}
        {% render child %}
      {% endfor %}
    </div>

For the slide, it's :file:`slideshow/templates/widgy/slideshow/slide/render.html`.

.. code-block:: html+django

    <img src="{{ self.image.url }}" alt="{{ self.caption }}">

.. seealso::

    :meth:`Content.get_templates_hierarchy <widgy.models.base.Content.get_templates_hierarchy>`
        Documentation for how templates are discovered.

The current ``Slideshow`` instance is available in the context as ``self``.
Because jQuery Cycle2 only accepts milliseconds instead of seconds for the
delay, we need to add a method to the ``Slideshow`` class. ::

    class Slideshow(Content):
        # ...
        def get_delay_milliseconds(self):
            return self.delay * 1000

The :class:`~widgy.models.base.Content` class mirrors several methods of the
:mod:`TreeBeard API <treebeard:treebeard.models>`, so you can call
:meth:`~widgy.models.base.Content.get_children` to get all the children. To
render a child :class:`~widgy.models.base.Content`, use the
:func:`~widgy.templatetags.widgy_tags.render` template tag.

.. caution::

    You might be tempted to include the HTML for each ``Slide`` inside the
    render template for ``Slideshow``. While this does work, it is a violation
    of the single responsibility principle and makes it difficult for slides
    (or subclasses thereof) to change how they are rendered.

.. _slideshow-compatibility:

3.  Write the Compatibility
---------------------------

Right now, the ``Slideshow`` and ``Slide`` render and could be considered
complete; however, the way we have it, ``Slideshow`` can accept any widget as a
child and a ``Slide`` can go in any parent. To disallow this, we have to write
some :ref:`Compatibility <compatibility>` methods. ::

    class Slideshow(Content):
        def valid_parent_of(self, cls, obj=None):
            # only accept Slides
            return issubclass(cls, Slide)

    class Slide(Content):
        @classmethod
        def valid_child_of(cls, parent, obj=None):
            # only go in Slideshows
            return isinstance(parent, Slideshow)


Done.

Addendum: Limit Number of Children
----------------------------------

Say you want to limit the number of ``Slide`` children to 3 for your
``Slideshow``. You do so like this::


    class Slideshow(Content):
        def valid_parent_of(self, cls, obj=None):
            if obj in self.get_children():
                # If it's already one of our children, it is valid
                return True
            else:
                # Make sure it's a Slide and that you aren't full
                return (issubclass(cls, Slide) and
                        len(self.get_children()) < 3)
