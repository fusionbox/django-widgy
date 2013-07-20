Template tags
-------------

To use these, you'll need to ``{% load widgy_tags %}``.

.. currentmodule:: widgy.templatetags.widgy_tags

.. function:: render(node)

Renders a node. Use this in your ``render.html`` templates to render children.
It's a template tag only to be able to be able to pass the current context to
:meth:`Content.render <widgy.models.Content.render>`

Example:

.. code-block:: html+django

    {% for child in self.get_children %}
      {% render child %}
    {% endfor %}

.. function:: scss_files(site)
.. function:: js_files(site)

A way to use all :attr:`WidgySite.scss_files <widgy.site.WidgySite.scss_files>`
and :attr:`~widgy.site.WidgySite.js_files` with a site determined from a setting.

.. code-block:: html+django

    {% for js_file in 'WIDGY_MEZZANINE_SITE'|js_files %}
      <script src="{% static js_file %}"></script>
    {% endfor %}

.. function:: render_root(owner, field_name)

The template entry point for rendering a tree. It delegates to
:meth:`WidgyField.render <widgy.db.fields.WidgyField.render>`. The
``root_node_override``  template context variable can be used to override the
root node that is rendered (for preview).

.. code-block:: html+django

    {% render_root owner_obj 'content' %}
