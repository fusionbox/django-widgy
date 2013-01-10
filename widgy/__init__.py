from django.core.exceptions import ImproperlyConfigured


class WidgetConfig(object):
    def __init__(self, site):
        self.site = site


class Registry(dict):
    def register(self, content, config=WidgetConfig):
        if content in self:
            raise ImproperlyConfigured("You cannot register the same content ('{0}') twice.".format(content))
        self[content] = config

    def unregister(self, content):
        del self[content]


registry = Registry()
