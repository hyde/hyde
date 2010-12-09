"""
Use nose
`$ pip install nose`
`$ nosetests`
"""

from hyde.fs import FS

def test_representation():
    f = FS(__file__)
    assert f.path == __file__
    assert str(f) == __file__
    assert repr(f) == __file__

def test_name():
    f = FS(__file__)
    assert f.name == "test_fs.py"

def test_name_without_extension():
    f = FS(__file__)
    assert f.name_without_extension == "test_fs"

def test_extension():
    f = FS(__file__)
    assert f.extension == ".py"

def test_kind():
    f = FS(__file__)
    assert f.kind == "py"