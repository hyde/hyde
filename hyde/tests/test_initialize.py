# -*- coding: utf-8 -*-
"""
Use nose
`$ pip install nose`
`$ nosetests`
"""


from hyde.engine import Engine
from hyde.exceptions import HydeException
from hyde.fs import FS, File, Folder

from nose.tools import raises, with_setup, nottest

TEST_SITE = File(__file__).parent.child_folder('_test')

@nottest
def create_test_site():
    TEST_SITE.make()

@nottest
def delete_test_site():
    TEST_SITE.delete()

@raises(HydeException)
@with_setup(create_test_site, delete_test_site)
def test_ensure_exception_when_sitepath_exists():
    e = Engine()
    e.run(e.parse(['-s', str(TEST_SITE), 'init']))

@with_setup(create_test_site, delete_test_site)
def test_ensure_no_exception_when_sitepath_exists_when_forced():
    e = Engine()
    e.run(e.parse(['-s', str(TEST_SITE), 'init', '-f']))
    assert True #No Exception

@with_setup(create_test_site, delete_test_site)
def test_ensure_no_exception_when_sitepath_does_not_exist():
    e = Engine()
    TEST_SITE.delete()
    e.run(e.parse(['-s', str(TEST_SITE), 'init', '-f']))
    assert TEST_SITE.exists
    assert TEST_SITE.child_folder('layout').exists
    assert File(TEST_SITE.child('info.yaml')).exists

