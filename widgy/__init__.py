from django.core.exceptions import ImproperlyConfigured
from django.db.models.base import ModelBase


def model_to_proxy(model_class, config_class):
    """
    Creates a new class that has mixes in the config class with the model.
    """
    return type(config_class.__name__, (config_class, model_class), {})


class WidgetConfigBase(ModelBase):
    """
    Don't do anything that ModelBase does in __new__.
    """
    def __new__(cls, name, bases, attrs):
        return type(object).__new__(cls, name, bases, attrs)


class WidgetConfig(object):
    """
    Implements a proxy object that will delegate to a model.  Additionally,
    this class is mixed into the model class making it possible to only treat
    self as the model.
    """
    __metaclass__ = WidgetConfigBase

    def __init__(self, model):
        self.model = model

    def __getattr__(self, key):
        return getattr(self.model, key)


class Registry(dict):
    def register(self, content, config=WidgetConfig):
        if content in self:
            raise ImproperlyConfigured("You cannot register the same content ('{0}') twice.".format(content))
        self[content] = model_to_proxy(content, config)

    def unregister(self, content):
        del self[content]


registry = Registry()
