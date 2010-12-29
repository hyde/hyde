# -*- coding: utf-8 -*-
"""
Use nose
`$ pip install nose`
`$ nosetests`
"""


from hyde.engine import Engine
from hyde.exceptions import HydeException
from hyde.fs import FS, File, Folder
from hyde.layout import Layout
from nose.tools import raises, with_setup, nottest

TEST_SITE = File(__file__).parent.child_folder('_test')
TEST_SITE_AT_USER = Folder('~/_test')

@nottest
def create_test_site():
    TEST_SITE.make()

@nottest
def delete_test_site():
    TEST_SITE.delete()

@nottest
def create_test_site_at_user():
    TEST_SITE_AT_USER.make()

@nottest
def delete_test_site_at_user():
    TEST_SITE_AT_USER.delete()

@raises(HydeException)
@with_setup(create_test_site, delete_test_site)
def test_ensure_exception_when_sitepath_exists():
    e = Engine()
    e.run(e.parse(['-s', str(TEST_SITE), 'create']))

@with_setup(create_test_site, delete_test_site)
def test_ensure_no_exception_when_sitepath_exists_when_forced():
    e = Engine()
    e.run(e.parse(['-s', str(TEST_SITE), 'create', '-f']))
    assert True #No Exception

@with_setup(create_test_site, delete_test_site)
def test_ensure_no_exception_when_sitepath_does_not_exist():
    e = Engine()
    TEST_SITE.delete()
    e.run(e.parse(['-s', str(TEST_SITE), 'create', '-f']))
    verify_site_contents(TEST_SITE, Layout.find_layout())

@with_setup(create_test_site_at_user, delete_test_site_at_user)
def test_ensure_can_create_site_at_user():
    e = Engine()
    TEST_SITE_AT_USER.delete()
    e.run(e.parse(['-s', str(TEST_SITE_AT_USER), 'create', '-f']))
    verify_site_contents(TEST_SITE_AT_USER, Layout.find_layout())

@nottest
def verify_site_contents(site, layout):
    assert site.exists
    assert site.child_folder('layout').exists
    assert File(site.child('info.yaml')).exists

    expected = map(lambda f: f.get_relative_path(layout), layout.walker.walk_all())
    actual = map(lambda f: f.get_relative_path(site), site.walker.walk_all())
    assert actual
    assert expected

    expected.sort()
    actual.sort()
    assert actual == expected

@raises(HydeException)
@with_setup(create_test_site, delete_test_site)
def test_ensure_exception_when_layout_is_invalid():
    e = Engine()
    e.run(e.parse(['-s', str(TEST_SITE), 'create', '-l', 'junk']))

