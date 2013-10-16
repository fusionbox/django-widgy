Customization
=============

.. outline customization options here, mention proxying


There are two main ways to customize the behavior of Widgy and existing widgets.
The first is through the :class:`~widgy.site.WidgySite`.
:class:`~widgy.site.WidgySite` is a centralized source of configuration for
a Widgy instance, much like Django's
:class:`~django:django.contrib.admin.AdminSite`.  You can also configure each
widget's behavior by subclassing it with a proxy.


WidgySite
---------

- tracks installed widgets
- stores URLs
- provides authorization
- allows centralized overriding of compatibility between components
- accomodates for multiple instances of widgy

Proxying a Widget
-----------------

Widgy uses a special subclass of
:class:`~django.contrib.contenttypes.generic.GenericForeignKey` that supports
retrieving proxy models.  Subclassing a model as a proxy is a lightweight method
for providing custom behavior for widgets that you don't control.  For example,
if you wanted to override the compatibility and ``verbose_name`` for Page
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
