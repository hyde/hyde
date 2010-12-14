from django.utils.html import strip_spaces_between_tags

def assert_html_equals(expected, actual):
    expected = strip_spaces_between_tags(expected.strip())
    actual = strip_spaces_between_tags(actual.strip())
    assert expected == actual
