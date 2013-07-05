Introduction
============

django-widgy is a heterogeneous tree editor for Django. It enables you to
combine different model of different types into a tree structure.

The django-widgy project is split into two main pieces. Widgy core provides
:class:`~widgy.models.Node`, the :class:`~widgy.models.Content` abstract class,
versioning models, views, configuration helpers, and the JavaScript editor
code. Much like in Django, django-widgy has many contrib packages that provide
the batteries.


Data Model
----------

Central to Widgy are Nodes, Contents, and Widgets. :class:`~widgy.models.Node`
is a subclass of Treebeard's :class:`~treebeard:treebeard.mp_tree.MP_Node`.
Nodes concern themselves with the tree structure. Each Node is associated with
an instance of :class:`~widgy.models.Content` subclass. A Node + Content
combination is called a Widget.

Storing all the structure data in Node and having that point to any subclass of
Content allows us to have all the benefits of a tree, but also the flexibility
to store very different data within a tree.

.. todo::

    Give an example, maybe something with this sort of diagram::

        Node (TwoColumnLayout)
        |
        +-- Node (MainBucket)
        |   |
        |   +-- Node (Text)
        |   |
        |   +-- Node (Image)
        |   |
        |   +-- Node (Form)
        |       |
        |       +-- Node (Input)
        |       |
        |       +-- Node (Checkboxes)
        |
        +-- Node (SidebarBucket)
            |
            +-- Node (CallToAction)


Editor
------

Widgy provides a drag and drop JavaScript editor interface to the tree in the
form of a Django formfield.

.. figure:: _images/interface-example.png
   :scale: 50 %
   :alt: Interface example

The editor is built on Backbone.js and RequireJS to provide a modular and
customizable interface.
