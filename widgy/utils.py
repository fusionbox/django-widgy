"""
Some utility functions used throughout the project.
"""


def path_generator(prefix, ext='.html'):
    """
    :Returns: a function that will return a path.

    >>> lol_genpath = path_generator('widgy/')
    >>> lol_genpath(lol, internet)
    'widgy/lol/internet.html'

    >>> lol_extensions = path_generator('widgy/', '.txt')
    >>> lol_extensions(lol, internet)
    'widgy/lol/internet.txt'
    """
    def inner(*args):
        return unicode(prefix) + u'/'.join(args) + ext
    return inner


def extract_id(url):
    """
    :Returns: the -2 index of a URL path.

    >>> extract_id('/bacon/eggs/')
    'bacon'
    """
    return url and url.split('/')[-2]


def exception_to_bool(fn):
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
        except:
            return False
    return new
