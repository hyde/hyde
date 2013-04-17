# -*- coding: utf-8 -*-
"""
Use nose
`$ pip install nose`
`$ nosetests`
"""
import os

from hyde.layout import Layout, HYDE_DATA, LAYOUTS

from fswrap import File
from nose.tools import nottest, with_setup

DATA_ROOT = File(__file__).parent.child_folder('data')
LAYOUT_ROOT = DATA_ROOT.child_folder(LAYOUTS)

@nottest
def setup_data():
    DATA_ROOT.make()

@nottest
def cleanup_data():
    DATA_ROOT.delete()

def test_find_layout_from_package_dir():
    f = Layout.find_layout()
    assert f.name == 'basic'
    assert f.child_folder('layout').exists

@with_setup(setup_data, cleanup_data)
def test_find_layout_from_env_var():
    f = Layout.find_layout()
    LAYOUT_ROOT.make()
    f.copy_to(LAYOUT_ROOT)
    os.environ[HYDE_DATA] = unicode(DATA_ROOT)
    f = Layout.find_layout()
    assert f.parent == LAYOUT_ROOT
    assert f.name == 'basic'
    assert f.child_folder('layout').exists
    del os.environ[HYDE_DATA]
