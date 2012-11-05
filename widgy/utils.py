def exception_to_bool(fn):
    """
    :Returns: wrapped function objects that caste exceptions to `False` and
    returns `True` otherwise.
    >>> exception_to_bool(lambda: True)()
    True
    >>> exception_to_bool(lambda: arst)()  #: NameError
    False
    """
    def new(*args, **kwargs):
        try:
            fn(*args, **kwargs)
            return True
        except:
            return False
    return new
