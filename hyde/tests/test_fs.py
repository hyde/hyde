# -*- coding: utf-8 -*-
"""
Use nose
`$ pip install nose`
`$ nosetests`
"""

from hyde.fs import FS, File, Folder
import codecs
import os


def test_representation():
    f = FS(__file__)
    assert f.path == __file__
    assert str(f) == __file__
    assert repr(f) == __file__

def test_name():
    f = FS(__file__)
    assert f.name == os.path.basename(__file__)

def test_name_without_extension():
    f = File(__file__)
    assert f.name_without_extension == "test_fs"

def test_extension():
    f = File(__file__)
    assert f.extension == os.path.splitext(__file__)[1]

def test_kind():
    f = File(__file__)
    assert f.kind == os.path.splitext(__file__)[1].lstrip('.')

def test_parent():
    f = File(__file__)
    p = f.parent
    assert hasattr(p, 'child_folder')
    assert str(p) == os.path.dirname(__file__)

def test_child():
    p = File(__file__).parent
    c = p.child('data.dat')
    assert c == os.path.join(os.path.dirname(__file__), 'data.dat')

def test_child_folder():
    p = File(__file__).parent
    c = p.child_folder('data')
    assert hasattr(c, 'child_folder')
    assert str(c) == os.path.join(os.path.dirname(__file__), 'data')


DATA_ROOT = File(__file__).parent.child_folder('data')

def test_read_all():
    utxt = u'åßcdeƒ'
    path = DATA_ROOT.child('unicode.txt')
    with codecs.open(path, 'w', 'utf-8') as f:
        f.write(utxt)

    txt = File(path).read_all()
    assert txt == utxt
    
def test_write():
    utxt = u'åßcdeƒ'
    path = DATA_ROOT.child('unicode.txt')
    File(path).write(utxt)
    txt = File(path).read_all()
    assert txt == utxt