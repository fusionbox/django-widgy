Base Models
===========

.. currentmodule:: widgy.models.base

.. class:: Content

    .. attribute:: node

        Accessor for the :class:`Node` that the :class:`Content` belongs to.

    .. rubric:: Tree Traversal

    With the exception :meth:`.depth_first_order`, the following methods are
    all like the traversal API provided by :mod:`Treebeard
    <treebeard:treebeard.models>`, but instead of returning :class:`Nodes
    <Node>`, they return :class:`Contents <Content>`.

    .. method:: get_root(self)

    .. method:: get_ancestors(self)

    .. method:: get_parent(self)

    .. method:: get_next_sibling(self)

    .. method:: get_children(self)

    .. method:: depth_first_order(self)

        Convenience method for iterating over all the :class:`Contents
        <Content>` in a subtree in order.  This is similar to Treebeard's
        :meth:`~treebeard:treebeard.models.Node.get_descendants`, but includes
        itself.

    .. rubric:: Tree Manipulation

    The following methods mirror those of :class:`Node`, but accept a
    :class:`~widgy.site.WidgySite` as the first argument.  You must call these
    methods on :class:`Content` and not on :class:`Node`. ::

        >>> root = Layout.add_root(widgy_site)
        >>> main = root.add_child(widgy_site, MainContent)
        >>> sidebar = main.add_sibling(widgy_site, Sidebar, title='Alerts')
        # move the sidebar to the left of the main content.
        >>> sidebar.reposition(widgy_site, right=main)

    .. classmethod:: add_root(cls, site, **kwargs)

        Creates a root node widget.  Any kwargs will be passed to the Content
        class's initialize method. ::

    .. method:: add_child(self, site, cls, **kwargs)

        Adds a new instance of ``cls`` as the last child of the current widget.

    .. method:: add_sibling(self, site, cls, **kwargs)

        Adds a new instance of ``cls`` to the right of the current widget.

    .. method:: reposition(self, site, right=None, parent=None)

        Moves the current widget to the left of ``right`` or to the last child
        position of ``parent``.

    .. method:: post_create(self, site)

        Hook for doing things after a widget has been created (a
        :class:`Content` has been created and put in the tree).  This is useful
        if you want to have default children for a widget, for example.

    .. method:: delete(self, raw=False)

        If ``raw`` is ``True`` the widget is being deleted due to a failure in
        widget creation, so ``post_create`` will not have been run yet.

    .. method:: clone(self)

        This method is called by :meth:`Node.clone_tree`.  You may wish to
        override it if your Content has special needs like a ManyToManyField.

        .. warning::

            Clone is used to freeze tree state in Versioning.  If your
            :meth:`.clone` method is incorrect, your history will be corrupt.

    .. rubric:: Editing

    .. attribute:: display_name

        A human-readable short name for widgets.  This defaults to the
        ``verbose_name`` of the widget.

        .. hint::

            You can use the ``@property`` decorator to make this dynamic.

        .. todo::

            screenshot

    .. attribute:: tooltip

        A class attribute that sets the tooltip for this widget on the shelf.

    .. attribute:: css_classes

        A list of CSS classes to apply to the widget element in the Editor.
        Defaults to ``app_label`` and ``module_name`` of the widget.

    .. attribute:: shelf = False

        Denotes whether this widget have a shelf.  Root nodes automatically
        have a shelf.  The shelf is where the widgets exist in the interface
        before they are dragged on.  It is useful to set :attr:`.shelf` to
        ``True`` if there are a large number of widgets who can only go in a
        specfic subtree.

    .. attribute:: component_name = 'widget'

        Specifies which JavaScript component to use for this widget.

        .. todo::

            Write documentation about components.

    .. attribute:: pop_out = CANNOT_POP_OUT

        It is possible to open a subtree in its own editing window.
        :attr:`.pop_out` controls if a widget can be popped out.  There are
        three values for :attr:`.pop_out`:

        .. attribute:: CANNOT_POP_OUT

        .. attribute:: CAN_POP_OUT

        .. attribute:: MUST_POP_OUT

    .. attribute:: form = ModelForm

        The form class to use for editing.  Also see :meth:`.get_form_class`.

    .. attribute:: formfield_overrides = {}

        Similar to :class:`~django:django.contrib.admin.ModelAdmin`,
        :class:`Content` allows you to override the form fields for specific
        model field classes.

    .. attribute:: draggable = True

        Denotes whether this widget may be moved through the editing interface.

    .. attribute:: deletable = True

        Denotes whether this widget may be deleted through the editing
        interface.

    .. attribute:: editable = False

        Denotes whether this widget may be edited through the editing
        interface.  Widgy will automatically generate a
        :class:`~django:django.forms.ModelForm` to provide the editing
        functionality.  Also see :attr:`.form` and :meth:`.get_form_class`.

    .. attribute:: preview_templates

        A template name or list of template names for rendering in the widgy
        Editor.  See :meth:`.get_templates_hierarchy` for how the default value
        is derived.

    .. attribute:: edit_templates

        A template name or list of template names for rendering the edit
        interface in the widgy Editor.  See :meth:`.get_templates_hierarchy`
        for how the default value is derived.

    .. method:: get_form_class(self, request)

        Returns a :class:`~django:django.forms.ModelForm` class that is used
        for editing.

    .. method:: get_form(self, request, **form_kwargs)

        Returns a form instance to use for editing.

    .. classmethod:: get_templates_hierarchy(cls, **kwargs)

        Loops through MRO to return a list of possible template names for a
        widget.  For example the preview template for something like
        :class:`~widgy.contrib.page_builder.models.Tabs` might look like:

        -  ``widgy/page_builder/tabs/preview.html``
        -  ``widgy/mixins/tabbed/preview.html``
        -  ``widgy/page_builder/accordion/preview.html``
        -  ``widgy/page_builder/bucket/preview.html``
        -  ``widgy/models/content/preview.html``
        -  ``widgy/page_builder/preview.html``
        -  ``widgy/mixins/preview.html``
        -  ``widgy/page_builder/preview.html``
        -  ``widgy/models/preview.html``
        -  ``widgy/preview.html``

    .. rubric:: Frontend Rendering

    .. method:: render(self, context, template=None)

        The method that is called by the
        :func:`~widgy.templatetags.widgy_tags.render` template tag to render
        the Content.  It is useful to override this if you need to inject
        things into the context.

    .. method:: get_render_templates(self, context)

        Returns a template name or list of template names for frontend
        rendering.

    .. _compatibility:

    .. rubric:: Compatibility

    Widgy provide robust machinery for compatibility between Contents.  Widgy
    uses the compatibility system to validate the relationships between parent
    and child Contents.

    Compatibility is checked when rendering the shelf and when adding or moving
    widgets in the tree.

    .. attribute:: accepting_children = False

        An easy compatibility configuration attribute.  See
        :meth:`.valid_parent_of` for more details.

    .. method:: valid_parent_of(self, cls, obj=None)

        If ``obj`` is provided, return ``True`` if it could be a child of the
        current widget.  ``cls`` is the type of ``obj``.

        If ``obj`` isn't provided, return ``True`` if a new instance of ``cls``
        could be a child of the current widget.

        ``obj`` is ``None`` when the child widget is being created or Widgy is
        checking the compatibility of the widgets on the shelf.  If it is being
        moved from another location, there will be an instance.  A parent and
        child are only compatible if both :meth:`.valid_parent_of` and
        :meth:`.valid_child_of` return ``True``.  This defaults to the value of
        :attr:`.accepting_children`.

        Here is an example of a parent that only accepts three instances of
        ``B``::

            class A(Content):
                def valid_parent_of(self, cls, obj=None):
                    # If this is already my child, it can stay my child.
                    # This works for obj=None because self.get_children()
                    # will never contain None.
                    if obj in self.get_children():
                        return True
                    else:
                        # Make sure it is of type B
                        return (issubclass(cls, B)
                        # And that I don't already have three children.
                            and len(self.get_children()) < 3)

    .. classmethod:: valid_child_of(cls, parent, obj=None)

        If ``obj`` is provided, return ``True`` if it can be a child of
        ``parent``.  ``obj`` will be an instance of ``cls``---it may feel like
        an instance method.

        If ``obj`` isn't provided, return ``True`` if a new instance of ``cls``
        could be a child of ``parent``.

        This defaults to ``True``.

        Here is an example of a Content that can not live inside another
        instance of itself::

            class Foo(Content):
                @classmethod
                def valid_child_of(cls, parent, obj=None):
                    for p in list(parent.get_ancestors()) + [parent]:
                        if isinstance(p, Foo):
                            return False
                    return super(Foo, cls).valid_child_of(parent, obj)

    .. method:: equal(self, other)

        Should return ``True`` if ``self`` is equal to ``other``. The default
        implementation checks the equality of each widget's
        :meth:`.get_attributes`.


.. class:: Node

    .. attribute:: content

        A generic foreign key point to our :class:`Content` instance.

    .. attribute:: is_frozen

        A boolean field indicating whether this node is frozen and can't be
        changed in any way. This is used to preserve old tree versions for
        versioning.

    .. method:: render(self, *args, **kwargs)

        Renders this subtree and returns a string. Normally you shouldn't
        call it directly, use :meth:`widgy.db.fields.WidgyField.render`
        or :func:`widgy.templatetags.widgy_tags.render`.

    .. method:: depth_first_order(self)

        Like :meth:`Content.depth_first_order`, but over nodes.

    .. method:: prefetch_tree(self)

        Efficiently fetches an entire tree (or subtree), including content
        instances. It uses ``1 + m`` queries, where ``m`` is the number of
        distinct content types in the tree.

    .. classmethod:: prefetch_trees(cls, *root_nodes)

        Prefetches multiple trees. Uses ``n + m`` queries, where ``n``
        is the number of trees and ``m`` is the number of distinct
        content types across `all` the trees.

    .. method:: maybe_prefetch_tree(self)

        Prefetches the tree unless it has been prefetched already.

    .. classmethod:: find_widgy_problems(cls, site=None)

        When a Widgy tree is edited without protection from a transaction, it is
        possible to get into an inconsistent state. This method returns a tuple
        containing two lists:

          1. A list of node pks whose `content` pointer is dangling --
             pointing to a content that doesn't exist.
          2. A list of node pks whose `content_type` doesn't exist. This might
             happen when you switch branches and remove the code for a widget,
             but still have the widget in your database. These are represented
             by :class:`UnknownWidget` instances.
