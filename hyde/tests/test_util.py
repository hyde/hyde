# -*- coding: utf-8 -*-
"""
Use nose
`$ pip install nose`
`$ nosetests`
"""

from hyde.util import load_python_object
import os

def test_can_load_locals():

    file_class = load_python_object('hyde.fs.File')
    assert file_class

    f = file_class(__file__)
    assert f

    assert f.name == os.path.basename(__file__)
