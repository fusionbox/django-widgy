Template Tags
-------------

To use these, you'll need to ``{% load widgy_tags %}``.

.. currentmodule:: widgy.templatetags.widgy_tags

.. function:: render(node)

Renders a node. Use this in your ``render.html`` templates to render any node
that isn't a root node.  Under the hood, this template tag calls
:meth:`Content.render <widgy.models.Content.render>` with the current context.

Example:

.. code-block:: html+django

    {% for child in self.get_children %}
      {% render child %}
    {% endfor %}

.. function:: scss_files(site)
.. function:: js_files(site)

These template tags provide a way to extract the :attr:`WidgySite.scss_files
<widgy.site.WidgySite.scss_files>` off of a site. This is required if you don't
have access to the site in the context, but do have a reference to it in your
settings file.  :func:`scss_files` and :func:`js_files` can also accept an
import path to the site.

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
