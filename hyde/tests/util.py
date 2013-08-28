import re
import difflib

def strip_spaces_between_tags(value):
    """
    Stolen from `django.util.html`
    Returns the given HTML with spaces between tags removed.
    """
    return re.sub(r'>\s+<', '><', unicode(value))

def assert_no_diff(expected, out):
    diff = [l for l in difflib.unified_diff(expected.splitlines(True),
                                                out.splitlines(True),
                                                n=3)]
    assert not diff, ''.join(diff)


def assert_html_equals(expected, actual, sanitize=None):
    expected = strip_spaces_between_tags(expected.strip())
    actual = strip_spaces_between_tags(actual.strip())
    if sanitize:
        expected = sanitize(expected)
        actual = sanitize(actual)
    assert expected == actual

def trap_exit_fail(f):
    def test_wrapper(*args):
        try:
            f(*args)
        except SystemExit:
            assert False
    test_wrapper.__name__ = f.__name__
    return test_wrapper

def trap_exit_pass(f):
    def test_wrapper(*args):
        try:
            f(*args)
        except SystemExit:
            pass
    test_wrapper.__name__ = f.__name__
    return test_wrapper