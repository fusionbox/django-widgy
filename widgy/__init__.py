import traceback
import sys

from django.core.exceptions import ImproperlyConfigured
from django.core.signals import request_started


class BaseRegistry(set):
    deferred_exception = None

    def register(self, model):
        from django.db import models
        if model in self:
            self.defer_exception(ImproperlyConfigured(
                "You cannot register the same model ('{0}') twice.".format(model)
            ))
        if not issubclass(model, models.Model):
            raise ImproperlyConfigured(("{0} is not a subclass of django.db.models.Model, "
                                        "so it cannot be registered").format(model))
        if model._meta.abstract:
            raise ImproperlyConfigured("You cannot register the abstract class {0}".format(model))
        self.add(model)

        # allow use as a decorator
        return model

    def unregister(self, model):
        try:
            self.remove(model)
        except KeyError as e:
            self.defer_exception(e)

    def defer_exception(self, exception):
        # XXX: this is a terrible hack to improve error reporting.
        #
        # Raising an exception here results in some awful error
        # reporting when models.py modules have ImportError. Django
        # will import the models module more than once, meaning
        # classes will get registered more than once, and if we
        # raise an exception here, you get an ImproperlyConfigured
        # instead of the ImportError that would help you find the
        # problem. See https://code.djangoproject.com/ticket/20839.
        self.deferred_exception = exception
        # sys._getframe(1) == skip defer_exception's frame, because it's
        # not interesting
        self.stacktrace = ''.join(traceback.format_stack(sys._getframe(1)))
        # We need an opportunity to raise the exception. Anything will
        # work as long as it happens after model loading. It'd be nice
        # if it happened during validation and didn't wait until the
        # first request, but there's no way to hook into that.
        #
        # The handler can't be registered in BaseRegistry.__init__
        # because the tests import this module before settings are
        # configured, and the signal can't be imported without settings.
        def handler(**kwargs):
            self.raise_deferred_exception()
            request_started.disconnect(handler)
        request_started.connect(handler, weak=False)

    def raise_deferred_exception(self):
        if self.deferred_exception:
            # six.reraise doesn't keep the whole stack, so print a
            # stacktrace to help find the error.
            sys.stderr.write(self.stacktrace)
            try:
                raise self.deferred_exception
            finally:
                self.deferred_exception = None


class Registry(BaseRegistry):
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
