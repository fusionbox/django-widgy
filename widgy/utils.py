"""
Some utility functions used throughout the project.
"""
from itertools import ifilterfalse
from contextlib import contextmanager

import bs4

from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from django.template import Context
from django.template.loader import select_template, get_template
from django.db import models
from django.db.models import query
from django.utils.http import urlencode
from django.utils.functional import memoize

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

try:
    from django.utils.encoding import force_text
    from django.utils.encoding import force_bytes
except ImportError:
    # Django 1.4
    from django.utils.encoding import force_unicode, smart_str
    force_bytes = smart_str
    force_text = force_unicode


def extract_id(url):
    """
    >>> extract_id('/bacon/eggs/')
    'eggs'
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
        path += '?' + urlencode(kwargs)
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
    # This only get the element having <elem role="main">, allowing
    # to index only the main text of the page.
    main = soup.find(role='main')
    if main:
        soup = main
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
    A Manager that makes it easy to always use prefetch_related or
    select_related. ::

        objects = SelectRelatedManager(select_related=['image'])

    """

    def __init__(self, *args, **kwargs):
        self.select_related = kwargs.pop('select_related', [])
        self.prefetch_related = kwargs.pop('prefetch_related', [])
        super(SelectRelatedManager, self).__init__(*args, **kwargs)

    def get_query_set(self, *args, **kwargs):
        qs = super(SelectRelatedManager, self).get_query_set(*args, **kwargs)
        return qs.select_related(*self.select_related).prefetch_related(*self.prefetch_related)


# Pending https://code.djangoproject.com/ticket/20806, Widgy's use of
# select_template is very slow (calling it many times with a long list
# of templates to choose from). Until it's fixed in Django, memoizing
# select_template has the same effect. It's OK to do this always,
# including DEBUG=False, because `memoize` doesn't cache exceptions. If
# memoize did cache exceptions, new templates wouldn't be discovered
# without restarting the server.
select_template = memoize(select_template, {}, 1)
def render_to_string(template_name, dictionary=None, context_instance=None):
    """
    Loads the given template_name and renders it with the given dictionary as
    context. The template_name may be a string to load a single template using
    get_template, or it may be a tuple to use select_template to find one of
    the templates in the list. Returns a string.
    """
    dictionary = dictionary or {}
    if isinstance(template_name, (list, tuple)):
        t = select_template(tuple(template_name))
    else:
        t = get_template(template_name)
    if not context_instance:
        return t.render(Context(dictionary))
    # Add the dictionary to the context stack, ensuring it gets removed again
    # to keep the context_instance in the same state it started in.
    with context_instance.push(dictionary):
        return t.render(context_instance)


if hasattr(models.Manager, 'from_queryset'):
    Manager = models.Manager
else:
    # Minimal and lazy backport of https://github.com/django/django/pull/1328
    class Manager(models.Manager):
        @classmethod
        def from_queryset(cls, queryset_class, class_name=None):
            if class_name is None:
                class_name = '%sFrom%s' % (cls.__name__,
                                           queryset_class.__name__)
            return type(class_name, (cls, ), {'_queryset_class': queryset_class})

        def get_queryset(self):
            return self._queryset_class(self.model, using=self.db)

        get_query_set = get_queryset # BBB

        def __getattr__(self, name):
            try:
                return super(Manager, self).__getattr__(name)
            except AttributeError:
                # Don't copy dunder methods
                if not name.startswith('_') and name not in ('delete', 'as_manager'):
                    attribute = getattr(self.get_queryset(), name, None)
                    if callable(attribute):
                        return attribute
                raise

if hasattr(query.QuerySet, 'as_manager'):
    QuerySet = query.QuerySet
else:
    # Minimal and lazy backport of https://github.com/django/django/pull/1328
    class QuerySet(query.QuerySet):
        @classmethod
        def as_manager(cls):
            return Manager.from_queryset(cls)()
