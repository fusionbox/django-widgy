Proxy Widgy Model Tutorial
=========================

Widgy was developed with a batteries included philosophy like Django.
When building your own widgy project, you may find that you need to change
the behavior of certain widgets. With :func:`widgy.unregister`, you can disable
existing widgy models and re-enable it with your custom proxy model
with :func:`widgy.register`.

This tutorial will cover a simple case where we add HTML classes to the
``<input>`` tags in the contrib module, Form Builder . This tutorial assumes
that you have a working widgy project. Please go through the
:doc:`widgy-mezzanine-tutorial` if you do not have a working project.

In a sample project, we are adding Bootstrap styling to our forms.
Widgy uses an easy template hierarchy to replace all of the
templates for styling; however, when we get to adding the styling class,
'form-control', to each of our input boxes in the forms, there is no
template to replace.

.. seealso::

    :meth:`Content.get_templates_hierarchy <widgy.models.base.Content.get_templates_hierarchy>`
        Documentation for how templates are discovered.

Widgy uses the power of Django to create a widget with predefined attributes.

To insert the class, you will need to override the attribute :attr:`widget_attrs`
in :class:`widgy.contrib.form_builder.models.FormInput`.
Start by creating a models.py file in your project and add your
project to the ``INSTALLED_APPS`` if you have not done so already.
Then add this to your models.py file::

    import widgy

    from widgy.contrib.form_builder.models import FormInput

    widgy.unregister(FormInput)

    @widgy.register
    class BootstrapFormInput(FormInput):

        class Meta:
            proxy = True
            verbose_name = 'Form Input'
            verbose_name_plural = 'Form Inputs'

        @property
        def widget_attrs(self):
            attrs = super(BootstrapFormInput, self).widget_attrs
            attrs['class'] = attrs.get('class', '') + ' form-control'
            return attrs

This code simply unregisters the existing FormInput and reregisters
our proxied version to replace the attribute :attr:`widget_attrs`.

To test it, simply create a form with a form input field and preview
it in the widgy interface. When you view the HTML source for that
field, you will see that the HTML class form-control is now added to ``<input>``.

In another example, if you wanted to override the compatibility and ``verbose_name`` for Page
Builder's :class:`~widgy.contrib.page_builder.models.CalloutBucket`, you could
do the following::

    import widgy
    from widgy.contrib.page_builder.models import CalloutBucket

    widgy.unregister(CalloutBucket)

    @widgy.register
    class MyCalloutBucket(CalloutBucket):
        class Meta:
            proxy = True
            verbose_name = 'Awesome Callout'

        def valid_parent_of(self, cls, obj=None):
            return issubclass(cls, (MyWidget)) or \
                super(MyCalloutBucket, self).valid_parent_of(self, cls, obj)


Finally, when using proxy models, if you proxy and unregister a model
that already has saved instances in the database, the old class will be used.
If you still need to use the existing widgets for the new proxy model,
you will need to write a database migration to update the content types.
Here is a sample of what may be required for this migration::

    Node.objects.filter(content_type=old_content_type).update(content_type=new_content_type)

More info on proxying models can be found on :ref:`Django's documentation on proxy
models <django:proxy-models>`
