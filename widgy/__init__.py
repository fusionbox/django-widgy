import traceback
import sys

from django.core.exceptions import ImproperlyConfigured


class BaseRegistry(set):
    """
    Container class for unique Django models.

    A model must be registered with a registry to be visible to Widgy.
    """
    def register(self, model):
        from django.db import models
        if model in self:
            raise ImproperlyConfigured(
                "You cannot register the same model ('{0}') twice."
                .format(model)
            )
        if not issubclass(model, models.Model):
            raise ImproperlyConfigured(("{0} is not a subclass of django.db.models.Model, "
                                        "so it cannot be registered").format(model))
        if model._meta.abstract:
            raise ImproperlyConfigured("You cannot register the abstract class {0}".format(model))
        self.add(model)

        # allow use as a decorator
        return model

    def unregister(self, model):
        self.remove(model)


class Registry(BaseRegistry):
    """
    Container class for all widgets available for use in widgy.

    A widget must be registered with the registry in order to appear in the
    available widgets box.
    """

    def register(self, content):
        from widgy.models import Content
        if not issubclass(content, Content):
            raise ImproperlyConfigured(
                "{0} is not a subclass of Content, so it cannot be registered".format(content)
            )
        return super(Registry, self).register(content)


registry = Registry()
register = registry.register
unregister = registry.unregister
