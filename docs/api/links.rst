:tocdepth: 1

Links Framework
===============

.. currentmodule:: widgy.models.links

Widgy core also provides a linking framework that allows any model to point to
any other model without really knowing which models are available for linking.
This is the mechanism by which Page Builder's
:class:`~widgy.contrib.page_builder.models.Button` can link to Widgy
Mezzanine's :class:`~widgy.contrib.widgy_mezzanine.models.WidgyPage` without
even knowing that ``WidgyPage`` exists. There are two components to the links
framework, :class:`~LinkField` and the link registry.

Model Field
-----------

.. class:: LinkField

    :class:`LinkField` is a subclass of
    :class:`django:django.contrib.contenttypes.generic.GenericForeignKey`. If
    you want to add a link to any model, you can just add a :class:`LinkField`
    to it. ::

        from django.db import models
        from widgy.models import links

        class MyModel(models.Model):
            title = models.Charfield(max_length=255)
            link = links.LinkField()

    :class:`LinkField` will automatically add the two required fields for
    GenericForeignKey, the
    :class:`~django:django.contrib.contenttypes.models.ContentType` ForeignKey
    and the PositiveIntegerField. If you need to override this, you can pass in
    the ``ct_field`` and ``fk_field`` options that GenericForeignKey takes.

.. note::

    Unfortunately, because Django currently lacks support for composite fields,
    if you need to display the :class:`LinkField` in a form, there are a couple
    of things you need to do.

    1.  Your Form class needs to mixin the :class:`LinkFormMixin`.

    2.  You need to explicitly define a :class:`LinkFormField` on your Form
        class.

    Hopefully in future iterations of Django, these steps will be obsoleted.

Registry
--------

If you want to expose your model to the link framework to allow things to link
to it, you need to do two things.

1.  You need to register your model with the links registry. ::

        from django.db import models
        from widgy.models import links

        class Blog(models.Model):
            # ...

        links.register(Blog)

    The :meth:`~LinkRegistry.register` function also works as a class
    decorator. ::

        from django.db import models
        from widgy.models import links

        @links.register
        class Blog(models.Model):
            # ...

2.  You need to make sure that your model defines a ``get_absolute_url``
    method.
