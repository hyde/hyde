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

