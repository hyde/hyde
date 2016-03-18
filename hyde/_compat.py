"""2/3 compatibility module for Hyde."""

# This module is for cross-version compatibility. As such, several
# assignments and import will look invalid to checkers like flake8.
# These lines are being marked with ``# NOQA`` to allow flake8 checking
# to pass.

import sys

PY3 = sys.version_info.major == 3

if PY3:
    # Imports that have moved.
    from collections import UserDict  # NOQA
    import configparser  # NOQA
    from functools import reduce  # NOQA
    from http.client import HTTPConnection, HTTPSConnection  # NOQA
    from http.server import HTTPServer, SimpleHTTPRequestHandler  # NOQA
    from io import StringIO  # NOQA
    from urllib import parse  # NOQA
    from urllib.parse import quote, unquote  # NOQA

    # Types that have changed name.
    filter = filter  # NOQA
    input = input  # NOQA
    str = str  # NOQA
    str = str  # NOQA
    zip = zip  # NOQA

    def execfile(filename, globals, locals):
        """Python 3 replacement for ``execfile``."""
        # Credit: 2to3 and this StackOverflow answer
        # (http://stackoverflow.com/a/437857/841994) take similar
        # approaches.
        with open(filename) as f:
            code = compile(f.read(), filename, 'exec')
            exec(code, globals, locals)

    def reraise(tp, value, tb=None):
        """Reraise exceptions."""
        if getattr(value, '__traceback__', tb) is not tb:
            raise value.with_traceback(tb)
        raise value

else:
    # Imports that have moved.
      # NOQA
    import configparser as configparser  # NOQA
    reduce = reduce
    from http.client import HTTPConnection, HTTPSConnection  # NOQA
    from http.server import HTTPServer  # NOQA
    from http.server import SimpleHTTPRequestHandler  # NOQA
    from io import StringIO  # NOQA
    from UserDict import IterableUserDict as UserDict  # NOQA
    import urllib.parse as parse  # NOQA
    from urllib.parse import quote, unquote  # NOQA

    # Types that have changed name.
    input = raw_input  # NOQA
    str = str  # NOQA
    str = str  # NOQA
    execfile = execfile  # NOQA

    exec('def reraise(tp, value, tb=None):\n raise tp, value, tb')


def iteritems(d):
    """Return iterable items from a dict."""
    if hasattr(d, 'iteritems'):
        return iter(d.items())
    else:
        return iter(list(d.items()))


def with_metaclass(meta, *bases):
    """Assign a metaclass in a 2/3 compatible fashion."""
    # Note: borrowed from https://github.com/dirn/Simon/
    # This requires a bit of explanation: the basic idea is to make a
    # dummy metaclass for one level of class instantiation that replaces
    # itself with the actual metaclass.  Because of internal type checks
    # we also need to make sure that we downgrade the custom metaclass
    # for one level to something closer to type (that's why __call__ and
    # __init__ comes back from type etc.).
    #
    # This has the advantage over six.with_metaclass in that it does not
    # introduce dummy classes into the final MRO.
    class metaclass(meta):
        __call__ = type.__call__
        __init__ = type.__init__

        def __new__(cls, name, this_bases, d):
            if this_bases is None:
                return type.__new__(cls, name, (), d)
            return meta(name, bases, d)
    return metaclass('DummyMetaClass', None, {})
