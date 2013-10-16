Design
======

django-widgy is a heterogeneous tree editor for Django. It enables you to
combine models of different types into a tree structure.

The django-widgy project is split into two main pieces. Widgy core provides
:class:`~widgy.models.Node`, the :class:`~widgy.models.Content` abstract class,
versioning models, views, configuration helpers, and the JavaScript editor
code. Much like in Django, django-widgy has many contrib packages that provide
the batteries.

.. toctree::
    :maxdepth: 1

    data-model
    versioning
    site
    owners
    javascript
