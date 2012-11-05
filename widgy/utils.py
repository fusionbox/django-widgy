"""
Some utility functions used throughout the project.
"""


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
