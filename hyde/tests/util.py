from django.utils.html import strip_spaces_between_tags

def assert_html_equals(expected, actual, sanitize=None):
    expected = strip_spaces_between_tags(expected.strip())
    actual = strip_spaces_between_tags(actual.strip())
    if sanitize:
        expected = sanitize(expected)
        actual = sanitize(actual)
    assert expected == actual