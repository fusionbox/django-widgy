"""
Some utility functions used throughout the project.
"""
import urllib

from contextlib import contextmanager
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from django.template import Context

try:
    from django.contrib.auth import get_user_model
except ImportError:
    def get_user_model():
        from django.contrib.auth.models import User
        return User

try:
    from django.utils.html import format_html
except ImportError:
    # Django < 1.5 doesn't have this

    def format_html(format_string, *args, **kwargs):  # NOQA
        """
        Similar to str.format, but passes all arguments through
        conditional_escape, and calls 'mark_safe' on the result. This function
        should be used instead of str.format or % interpolation to build up
        small HTML fragments.
        """
        args_safe = map(conditional_escape, args)
        kwargs_safe = dict([(k, conditional_escape(v)) for (k, v) in kwargs.iteritems()])
        return mark_safe(format_string.format(*args_safe, **kwargs_safe))


def extract_id(url):
    """
    :Returns: the -2 index of a URL path.

    >>> extract_id('/bacon/eggs/')
    'bacon'
    """
    return url and url.split('/')[-2]


def exception_to_bool(fn, exception=Exception):
    """
    :Returns: wrapped function objects that caste exceptions to `False`
        and returns `True` otherwise.

    >>> exception_to_bool(lambda: True)()
    True
    >>> exception_to_bool(lambda: arst)()  # NameError
    False
    """
    def new(*args, **kwargs):
        try:
            fn(*args, **kwargs)
            return True
        except exception:
            return False
    return new


def fancy_import(name):
    """
    This takes a fully qualified object name, like 'accounts.models.ProxyUser'
    and turns it into the accounts.models.ProxyUser object.
    """
    import_path, import_me = name.rsplit('.', 1)
    imported = __import__(import_path, globals(), locals(), [import_me], -1)
    return getattr(imported, import_me)


@contextmanager
def update_context(context, dict):
    if context is None:
        context = {}
    if not isinstance(context, Context):
        context = Context(context)
    context.update(dict)
    yield context
    context.pop()

def build_url(path, **kwargs):
    if kwargs:
        path += '?' + urllib.urlencode(kwargs)
    return path
