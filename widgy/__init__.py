from django.core.exceptions import ImproperlyConfigured


class Registry(dict):
    def register(self, content):
        if content in self:
            raise ImproperlyConfigured("You cannot register the same content ('{0}') twice.".format(content))
        self[content] = True

    def unregister(self, content):
        del self[content]


registry = Registry()
