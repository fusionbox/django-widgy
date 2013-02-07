from django.core.exceptions import ImproperlyConfigured


class Registry(dict):
    def register(self, content):
        from widgy.models import Content
        if content in self:
            raise ImproperlyConfigured("You cannot register the same content ('{0}') twice.".format(content))
        if content._meta.abstract:
            raise ImproperlyConfigured("You cannot register the abstract class {0}".format(content))
        if not issubclass(content, Content):
            raise ImproperlyConfigured("{0} is not a subclass of Content, so it cannot be registered".format(content))
        self[content] = True

        # allow use as a decorator
        return content

    def unregister(self, content):
        del self[content]


registry = Registry()
register = registry.register
