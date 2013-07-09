Widgy Site
==========


.. currentmodule:: widgy.site

.. class:: WidgySite

    .. attribute:: scss_files

    .. attribute:: js_files

    .. attribute:: admin_scss_files

    .. method:: get_registry(self)

    .. method:: get_all_content_classes(self)

    .. method:: get_urls(self)

    .. method:: urls(self)

    .. method:: reverse(self, *args, **kwargs)

    .. method:: get_view_instance(self, view)

    .. method:: authorize_view(self, request, view)

    .. method:: has_add_permission(self, request, content_class)

    .. method:: has_change_permission(self, request, obj_or_class)

    .. method:: has_delete_permission(self, request, obj_or_class)

    .. method:: node_view(self)

    .. method:: content_view(self)

    .. method:: shelf_view(self)

    .. method:: node_edit_view(self)

    .. method:: node_templates_view(self)

    .. method:: node_parents_view(self)

    .. method:: commit_view(self)

    .. method:: history_view(self)

    .. method:: revert_view(self)

    .. method:: diff_view(self)

    .. method:: reset_view(self)

    .. method:: valid_parent_of(self, parent, child_class, child=None)

    .. method:: valid_child_of(self, parent, child_class, child=None)

    .. method:: validate_relationship(self, parent, child)

    .. method:: get_version_tracker_model(self)

    .. method:: filter_existing_staticfiles(self, filename)

    .. method:: find_media_files(self, extension, hierarchy=['widgy/{app_label}/{module_name}{extension}'])
