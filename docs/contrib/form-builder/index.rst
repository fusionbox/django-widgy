Form Builder
============

Form builder is a collection of tools built on top of Page Builder that help
with the creation of HTML forms.

.. form_builder does actually rely on Html existing.

To enable Form Builder, add ``widgy.contrib.form_builder`` to
your :django:setting:`INSTALLED_APPS`.


.. currentmodule:: widgy.contrib.form_builder.models

Installation
------------

Form builder depends on the following packages:

* django-widgy[page_builder]
* django-extensions
* html2text
* phonenumbers

You can install them manually, or you can install them using the django-widgy
package::

    $ pip install django-widgy[page_builder,form_builder]

Success Handlers
----------------

When a user submits a :class:`Form`, the :class:`Form` will loop through all of
the success handler widgets to do the things that you would normally put in the
``form_valid`` method of a :class:`~django:django.views.generic.FormView`, for
example.  Form Builder provides a couple of built-in success handlers that do
things like saving the data, sending emails, or submitting to Salesforce.


Widgets
-------

.. class:: Form

    This widget corresponds to the HTML ``<form>`` tag. It acts as a container
    and also can be used to construct a Django Form class.

    .. method:: build_form_class(self)

        Returns a Django Form class based on the FormField widgets inside the
        form.


.. class:: Uncaptcha


.. class:: FormField

    :class:`FormField` is an abstract base class for the following widgets.
    Each :class:`FormField` has the following fields which correspond to the
    same attributes on :class:`django:django.forms.fields.Field`.

    .. attribute:: label

        Corresponds with the HTML ``<label>`` tag. This is the text that will
        go inside the label.

    .. attribute:: required

        Indicates whether or not this field is required. Defaults to True.

    .. attribute:: help_text

        A TextField for outputting help text.


.. class:: FormInput

    This is a widget for all simple ``<input>`` types. It supports the
    following input types: ``text``, ``number``, ``email``, ``tel``,
    ``checkbox``, ``date``. Respectively they correspond with the following
    Django formfields: :class:`~django:django.forms.CharField`,
    :class:`~django:django.forms.IntegerField`,
    :class:`~django:django.forms.EmailField`, ``PhoneNumberField``,
    :class:`~django:django.forms.BooleanField`,
    :class:`~django:django.forms.DateField`.

.. class:: Textarea


.. class:: ChoiceField


.. class:: MultipleChoiceField


Owner Contract
--------------

For custom :ref:`Widgy owners <owners>`, Form Builder needs to have a
view to use for handling form submissions.

1.  Each widgy owner should implement a
    ``get_form_action_url(form, widgy_context)`` method that returns a
    URL that points to a view (see step 2).

2.  Create a view to handle form submissions for each owner. Form Builder provides the
    class-based views mixin,
    :class:`~widgy.contrib.form_builder.views.HandleFormMixin`, to make this
    easier.


Views
-----

.. class:: widgy.contrib.form_builder.views.HandleFormMixin

    An abstract view mixin for handling form_builder.Form submissions. It
    inherits from
    :class:`django.views.generic.edit.FormMixin`.

    It should be registered with a URL similar to the following. ::

        url('^form/(?P<form_node_pk>[^/]*)/$', 'your_view')


    :class:`~widgy.contrib.form_builder.views.HandleFormMixin` does not
    implement a GET method, so your subclass should handle that.  Here is an
    example of a fully functioning implementation::

        from django.views.generic import DetailView
        from widgy.contrib.form_builder.views import HandleFormMixin

        class EventDetailView(HandleFormMixin, DetailView):
            model = Event

            def post(self, *args, **kwargs):
                self.object = self.get_object()
                return super(EventDetailView, self).post(*args, **kwargs)

    :class:`widgy.contrib.widgy_mezzanine.views.HandleFormView` provides an
    even more robust example implementation.
