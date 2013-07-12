Base Models
===========

.. currentmodule:: widgy.models.base

.. class:: Content

    .. attribute:: draggable = True

    .. attribute:: deletable = True

    .. attribute:: editable = False

    .. attribute:: accepting_children = False

    .. attribute:: shelf = False

    .. attribute:: component_name = 'widget'

    .. attribute:: pop_out = CANNOT_POP_OUT

        .. attribute:: CANNOT_POP_OUT

        .. attribute:: CAN_POP_OUT

        .. attribute:: MUST_POP_OUT

    .. attribute:: form = ModelForm

    .. attribute:: formfield_overrides = {}

    .. attribute:: node

    .. attribute:: class_name

    .. attribute:: display_name


    .. method:: to_json(self, site)

    .. method:: get_attributes(self)

    .. classmethod:: class_to_json(cls, site)

    .. method:: css_classes(self)

    .. method:: get_root(self)

    .. method:: get_ancestors(self)

    .. method:: depth_first_order(self)

    .. method:: get_children(self)

    .. method:: get_next_sibling(self)

    .. method:: get_parent(self)

    .. method:: get_form_class(self, request)

    .. method:: get_form(self, request, **form_kwargs)

    .. method:: valid_parent_of(self, cls, obj=None)

    .. classmethod:: valid_child_of(cls, parent, obj=None)

    .. classmethod:: add_root(cls, site, **kwargs)

    .. method:: add_child(self, site, cls, **kwargs)

    .. method:: add_sibling(self, site, cls, **kwargs)

    .. method:: post_create(self, site)

    .. classmethod:: get_templates_hierarchy(cls, **kwargs)

    .. classmethod:: get_template_kwargs(cls, **kwargs)

    .. method:: preview_templates(self)

    .. method:: edit_templates(self)

    .. method:: get_render_templates(self, context)

    .. method:: get_form_template(self, request, template=None, context=None)

    .. method:: get_preview_template(self, site)

    .. method:: render(self, context, template=None)

    .. method:: formfield_for_dbfield(self, db_field, **kwargs)

    .. method:: get_templates(self, request)

    .. method:: reposition(self, site, right=None, parent=None)

    .. method:: delete(self, raw=False)

    .. method:: clone(self)

    .. method:: save(self, *args, **kwargs)


.. class:: Node

    .. attribute:: content

    .. attribute:: is_frozen

    .. method:: to_json(self, site)

    .. method:: render(self, *args, **kwargs)

    .. method:: depth_first_order(self)

    .. classmethod:: prefetch_trees(cls, *root_nodes)

    .. method:: prefetch_tree(self)

    .. method:: maybe_prefetch_tree(self)

    .. method:: filter_child_classes(self, site, classes)

    .. method:: filter_child_classes_recursive(self, site, classes)

    .. method:: possible_parents(self, site, root_node)

    .. method:: clone_tree(self, freeze=True)

    .. method:: check_frozen(self)

    .. method:: delete(self, *args, **kwargs)

    .. method:: trees_equal(self, other)

    .. classmethod:: find_widgy_problems(cls, site=None)
