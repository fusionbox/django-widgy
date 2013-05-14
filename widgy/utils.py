"""
Some utility functions used throughout the project.
"""
import urllib
from itertools import ifilterfalse

import bs4
from contextlib import contextmanager
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from django.template import Context
from django.db import models

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


def html_to_plaintext(html):

    def get_text(node):
        IGNORED_TAGS = ['script', 'style', 'head']
        INDEXED_ATTRIBUTES = ['title', 'alt']
        if node.name in IGNORED_TAGS:
            pass
        else:
            for c in node.children:
                if isinstance(c, unicode):
                    if not isinstance(c, bs4.Comment):
                        yield c.strip()
                elif isinstance(c, bs4.Tag):
                    for attr in INDEXED_ATTRIBUTES:
                        if c.has_attr(attr):
                            yield c[attr]
                    for t in get_text(c):
                        yield t

    soup = bs4.BeautifulSoup(html)
    text = ' '.join(get_text(soup))
    return text


def unique_everseen(iterable, key=None):
    "List unique elements, preserving order. Remember all elements ever seen."
    # http://docs.python.org/2/library/itertools.html
    seen = set()
    seen_add = seen.add
    if key is None:
        for element in ifilterfalse(seen.__contains__, iterable):
            seen_add(element)
            yield element
    else:
        for element in iterable:
            k = key(element)
            if k not in seen:
                seen_add(k)
                yield element


class SelectRelatedManager(models.Manager):
    """
    A Manager that always uses select_related.
    """

    def __init__(self, *args, **kwargs):
        self.select_related = kwargs.pop('select_related', [])
        super(SelectRelatedManager, self).__init__(*args, **kwargs)

    def get_query_set(self, *args, **kwargs):
        qs = super(SelectRelatedManager, self).get_query_set(*args, **kwargs)
        return qs.select_related(*self.select_related)
