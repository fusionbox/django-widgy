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
for providing custom behavior for widgets that you don't control.
A more in-depth tutorial on proxying widgets can be found at the
:doc:`../tutorials/proxy-widget`.
