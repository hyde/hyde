from django.utils.html import strip_spaces_between_tags

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
            print f.__name__
            f(*args)
        except SystemExit:
            pass
    test_wrapper.__name__ = f.__name__
    return test_wrapper