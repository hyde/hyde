"""
Module for python 2.6 compatibility.
"""
import os
from functools import partial
from itertools import izip, tee


def make_method(method_name, method_):
    def method__(*args, **kwargs):
        return method_(*args, **kwargs)
    method__.__name__ = method_name
    return method__


def add_property(obj, method_name, method_, *args, **kwargs):
    m = make_method(method_name, partial(method_, *args, **kwargs))
    setattr(obj, method_name, property(m))


def add_method(obj, method_name, method_, *args, **kwargs):
    m = make_method(method_name, partial(method_, *args, **kwargs))
    setattr(obj, method_name, m)


def pairwalk(iterable):
    a, b = tee(iterable)
    next(b, None)
    return izip(a, b)


def first_match(predicate, iterable):
    """
    Gets the first element matched by the predicate
    in the iterable.
    """
    for item in iterable:
        if predicate(item):
            return item
    return None


def discover_executable(name, sitepath):
    """
    Finds an executable in the given sitepath or in the
    path list provided by the PATH environment variable.
    """

    # Check if an executable can be found in the site path first.
    # If not check the os $PATH for its presence.

    paths = [unicode(sitepath)] + os.environ['PATH'].split(os.pathsep)
    for path in paths:
        full_name = os.path.join(path, name)
        if os.path.exists(full_name):
            return full_name
    return None