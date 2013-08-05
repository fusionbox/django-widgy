.. _owners:

Owners
======

A Widgy owner is a model that has a :class:`~widgy.db.fields.WidgyField`.

Admin
-----

Use :class:`~widgy.admin.WidgyAdmin` (or a :class:`~widgy.forms.WidgyForm` for
your admin form)

Use ``get_action_links`` to add a preview button to the editor.


Page Builder
------------
If layouts should extend something other than ``layout_base.html``, set the
``base_template`` property on your owner.


Form Builder
------------
``widgy.contrib.form_builder`` requires a ``get_form_action`` method on the
owner. It accepts the form widget and the Widgy context, and returns a URL for
forms to submit to. You normally submit to your own view and mix in
:class:`~widgy.contrib.form_builder.views.HandleFormMixin` to help with handling
the form submission.  Make sure re-rendering after a validation error works.


.. todo::

    tutorials/owner


Tutorial
--------
  - It's probably a good idea to render the entire page through Widgy, so I've
    used a template like this:

    .. code-block:: html+django

        {# product_list.html #}

        {% include widgy_tags %}{% render_root category 'content' %}

    I have been inserting the 'view' style functionality, in this case a list
    of products in a category, with ``ProductList`` widget.


You'll probably have to add support for ``root_node_override`` to your view,
like this::

    root_node_pk = self.kwargs.get('root_node_pk')
    if root_node_pk:
        site.authorize_view(self.request, self)
        kwargs['root_node_override'] = get_object_or_404(Node, pk=root_node_pk)
    elif hasattr(self, 'form_node'):
        kwargs['root_node_override'] = self.form_node.get_root()
