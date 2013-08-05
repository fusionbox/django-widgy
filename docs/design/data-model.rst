Data Model
==========

Central to Widgy are Nodes, Contents, and Widgets. :class:`~widgy.models.Node`
is a subclass of Treebeard's :class:`~treebeard:treebeard.mp_tree.MP_Node`.
Nodes concern themselves with the tree structure. Each Node is associated with
an instance of :class:`~widgy.models.Content` subclass. A Node + Content
combination is called a Widget.

Storing all the structure data in Node and having that point to any subclass of
Content allows us to have all the benefits of a tree, but also the flexibility
to store very different data within a tree.

:class:`Nodes <widgy.models.Node>` are associated with their
:class:`~widgy.models.Content` through a
:class:`~django:django.contrib.contenttypes.generic.GenericForeignKey`.

This is what a hypothetical Widgy tree might look like.::

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
    |       |
    |       +-- Node (SubmitButton)
    |
    +-- Node (SidebarBucket)
        |
        +-- Node (CallToAction)
