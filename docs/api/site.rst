Widgy Site
==========

.. currentmodule:: widgy.site

.. class:: WidgySite

    .. method:: get_all_content_classes(self)

    Returns a list (or set) of available Content classes (widget
    classes). This is used

        - To find layouts from :attr:`~widgy.db.fields.WidgyField.root_choices`

        - To find widgets to put on the shelf (using
          :meth:`validate_relationship` against all existing widgets in
          a tree)

    .. method:: urls(self)

    Returns the urlpatterns needed for this Widgy site. It should be
    included in your urlpatterns::

        ('^admin/widgy/', include(widgy_site.urls)),

    .. method:: get_urls(self)

    This method only exists due to the example
    :class:`~django:django.contrib.admin.ModelAdmin` sets.

      .. todo:: is ``urls`` or ``get_urls`` the preferred interface?

    .. method:: reverse(self, *args, **kwargs)

      .. todo:: explain reverse

    .. method:: authorize_view(self, request, view)

    Every Widgy view will call this before doing anything. It can
    be considered a 'view' or 'read' permission. It should raise a
    :exc:`~django:django.core.exceptions.PermissionDenied` when the
    request is not authorized. It can be used to implement permission
    checking that should happen on every view, like limiting access to
    staff members::

      def authorize_view(self, request, view):
          if not request.user.is_staff:
              raise PermissionDenied
          super(WidgySite, self).authorize_view(request, value)

    .. method:: has_add_permission(self, request, content_class)

    Given a :class:`~widgy.models.Content` class, can this request add a new
    instance? Returns ``True`` or ``False``.  The default implementation uses
    the Django Permission framework.

    .. method:: has_change_permission(self, request, obj_or_class)

    Like :meth:`~WidgySite.has_add_permission`, but for changing. It receives an instance if
    one is available, otherwise a class.

    .. method:: has_delete_permission(self, request, obj_or_class_or_list)

    Like :meth:`~WidgySite.has_change_permission`, but for deleting.
    ``obj_or_class_or_list`` can also be a list, when attempting to delete a
    widget that has children.

    .. method:: validate_relationship(self, parent, child)

    The single compatibility checking entry point. The default
    implementation delegates to :meth:`~.valid_parent_of` of
    :meth:`~.valid_child_of`.

    ``parent`` is always an instance, ``child`` can be a class or an instance.

    .. method:: valid_parent_of(self, parent, child_class, child=None)

    Does ``parent`` accept the ``child`` instance, or a new
    ``child_class`` instance, as a child?

    The default implementation just delegates to
    :meth:`Content.valid_parent_of <widgy.models.Content.valid_parent_of>`.

    .. method:: valid_child_of(self, parent, child_class, child=None)

    Will the ``child`` instance, or a new instance of ``child_class``,
    accept ``parent`` as a parent?

    The default implementation just delegates to
    :meth:`Content.valid_child_of <widgy.models.Content.valid_child_of>`.

    .. method:: get_version_tracker_model(self)

    Returns the class to use as a :class:`~widgy.models.VersionTracker`.
    This can be overridden to customize versioning behavior.

    .. method:: valid_root_of(self, owner_field, root_class, root_choices)

    Is ``root_class`` a valid root choice for ``owner_field`` given the full
    set of available ``root_choices``? This can be overridden to customize the
    available layouts for the :class:`widgy.site.WidgySite`.

    .. rubric:: Views

    Each of these properties returns a view callable. A urlpattern is built in
    :meth:`.get_urls`. It is important that the same callable is used for the
    lifetime of the site, so
    :func:`~django:django.utils.functional.cached_property` is helpful.

    .. attribute:: node_view(self)

    .. attribute:: content_view(self)

    .. attribute:: shelf_view(self)

    .. attribute:: node_edit_view(self)

    .. attribute:: node_templates_view(self)

    .. attribute:: node_parents_view(self)

    .. attribute:: commit_view(self)

    .. attribute:: history_view(self)

    .. attribute:: revert_view(self)

    .. attribute:: diff_view(self)

    .. attribute:: reset_view(self)


    .. rubric:: Media Files

    .. note::
        These properties are cached at server start-up, so new ones
        won't be detected until the server restarts. This means that
        when using ``runserver``, you have to manually restart the
        server when adding a
        new file.

    .. attribute:: scss_files

    Returns a list of SCSS files to be included on the front-end.
    Widgets can add SCSS files just by making a file available
    at a location determined by its app label and name (see
    :func:`widgy.models.Content.get_templates_hierarchy`). For example::

          widgy/page_builder/html.scss

    .. attribute:: js_files

       Like ``scss_files``, but JavaScript files.

    .. attribute:: admin_scss_files

      Like ``scss_files``, but for the back-end editing interface. These
      paths look like, for an app::

          widgy/page_builder/admin.scss

      and for a widget::

          widgy/page_builder/table.admin.scss

      If you want to included JavaScript for the editing interface, you should
      use a :attr:`component <widgy.models.base.Content.component_name>`.
