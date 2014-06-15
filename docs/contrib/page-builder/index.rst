Page Builder
============

.. currentmodule:: widgy.contrib.page_builder.models

Page builder is a collection of widgets for the purpose of creating HTML pages.

Installation
------------

Page builder depends on the following packages:

* django-filer
* markdown
* bleach
* sorl-thumbnail

You can install them manually, or you can install them using the django-widgy
package::

    $ pip install django-widgy[page_builder]


Widgets
-------


.. class:: DefaultLayout

    .. todo::

        Who actually uses DefaultLayout?


.. class:: MainContent


.. class:: Sidebar


.. class:: Markdown


.. class:: Html

    The HTML Widget provides a CKEditor field. It is useful for large blocks of
    text that need simple inline styling. It purposefully doesn't have the
    capability to add images or tables, because there are already widgets that
    the developer can control.

    .. note::

        There is a possible permission escalation vulnerability with allowing
        any admin user to add HTML. For this reason, the :class:`Html` widget
        sanitizes all the HTML using bleach_. If you want to add unsanitized
        HTML, please use the :class:`UnsafeHtml` widget.

.. class:: UnsafeHtml

    This is a widget which allows the user to output arbitrary HTML. It is
    unsafe because a non-superuser could gain publishing the unsafe HTML on the
    website with XSS code to cause permission escalation.

    .. warning::

        The ``page_builder.add_unsafehtml`` and ``page_builder.edit_unsafehtml``
        permissions are equivalent to ``is_superuser`` status because of the
        possibility of a staff user inserting JavaScript that a superuser will
        execute.

.. class:: CalloutWidget


.. class:: Accordion


.. class:: Tabs


.. class:: Section


.. class:: Image


.. class:: Video


.. class:: Figure


.. class:: GoogleMap


.. class:: Button


Tables
------

.. class:: Table


.. class:: TableRow


.. class:: TableHeaderData


.. class:: TableData


.. _bleach: https://pypi.python.org/pypi/bleach


Database Fields
---------------

.. currentmodule:: widgy.contrib.page_builder.db.fields

.. class:: ImageField

    A :filer:ref:`FilerFileField <usage>` that only accepts
    images. Includes sensible defaults for use in Widgy --- ``null=True``,
    ``related_name='+'`` and ``on_delete=PROTECT``.
