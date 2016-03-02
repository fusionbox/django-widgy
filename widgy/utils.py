"""
Some utility functions used throughout the project.
"""
import warnings
from six.moves import filterfalse
from contextlib import contextmanager
from functools import wraps
import six

import bs4

from django.template import Context
from django.db import models
from django.db.models import query
from django.utils.http import urlencode
from django.http.request import QueryDict

from django.contrib.auth import get_user_model
from django.utils.html import format_html
from django.utils.encoding import force_text, force_bytes


def deprecate(fn):
    @wraps(fn)
    def new(*args, **kwargs):
        warnings.warn(
            "widgy.utils.{} is deprecated. Use the version from {} instead.".format(
                fn.__name__,
                fn.__module__
            ),
            DeprecationWarning,
            stacklevel=2,
        )
        return fn(*args, **kwargs)
    return new

get_user_model = deprecate(get_user_model)
format_html = deprecate(format_html)
force_text = deprecate(force_text)
force_bytes = deprecate(force_bytes)


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
    imported = __import__(import_path, globals(), locals(), [import_me])
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


def build_url(path, *args, **kwargs):
    if args:
        if len(args) != 1:
            raise TypeError("Length of args must be exactly 1.")
        if kwargs:
            raise TypeError("You may not specify both args and kwargs.")

        arg = args[0]
        if len(arg):
            if isinstance(arg, QueryDict):
                path += '?' + arg.urlencode()
            else:
                path += '?' + urlencode(args[0])

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
                if isinstance(c, six.string_types):
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
        for element in filterfalse(seen.__contains__, iterable):
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
        self._select_related = kwargs.pop('select_related', [])
        self._prefetch_related = kwargs.pop('prefetch_related', [])
        super(SelectRelatedManager, self).__init__(*args, **kwargs)

    def get_queryset(self, *args, **kwargs):
        qs = super(SelectRelatedManager, self).get_queryset(*args, **kwargs)
        return qs.select_related(*self._select_related).prefetch_related(*self._prefetch_related)


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


def unset_pks(obj):
    """
    Unsets the pk field of a model, including its parent's pks during
    multi-table inheritance. Normally we would say

       obj.pk = None
       obj.id = None

    but we can't know for sure what the name of the actually primary key field
    is called.  So we do this to set all the primary keys to None.
    """
    for field in obj._meta.fields:
        if field.primary_key:
            setattr(obj, field.attname, None)


def model_has_field(cls, field_name):
    """
    Check if a field is already present on a model in a `safe` manner that does
    not trigger or violate application loading.
    """
    exists = field_name in [f.name for f in cls._meta.local_fields]
    if exists:
        return exists
    elif cls._meta.parents:
        return any((
            model_has_field(parent, field_name) for parent in cls._meta.parents.keys()
        ))
    else:
        return False
