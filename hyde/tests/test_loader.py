# -*- coding: utf-8 -*-
"""
Use nose
`$ pip install nose`
`$ nosetests`
"""

from hyde.loader import load_python_object
from nose.tools import raises
import os

from hyde.exceptions import HydeException
from hyde.fs import File, Folder
from hyde.generator import Generator
from hyde.site import Site



def test_can_load_locals():

    file_class = load_python_object('hyde.fs.File')
    assert file_class

    f = file_class(__file__)
    assert f

    assert f.name == os.path.basename(__file__)


def test_can_load_from_python_path():

    markdown = load_python_object('markdown.markdown')
    assert markdown

    assert "<h3>h3</h3>" == markdown("### h3")

def test_can_load_module_without_dot():

    yaml = load_python_object('yaml')

    abc = yaml.load("""
        d: efg
        l: mno
    """)

    assert abc['d'] == 'efg'
    assert abc['l'] == 'mno'

def test_can_load_site_specific_plugins():
    
    TEST_SITE = File(__file__).parent.child_folder('_test')
    TEST_SITE.make()
    TEST_SITE.parent.child_folder(
                  'sites/test_jinja').copy_contents_to(TEST_SITE)
    TEST_SITE.parent.child_folder(
                  'ssp').copy_contents_to(TEST_SITE)
    s = Site(TEST_SITE)
    gen = Generator(s)
    gen.generate_all()
    banner = """
<!--
This file was produced with infinite love, care & sweat.
Please dont copy. If you have to, please drop me a note.
-->
"""
    with TEST_SITE.child_folder('deploy').get_walker('*.html') as walker:
        
        @walker.file_visitor
        def visit_file(f):
            text = f.read_all()
            assert text.strip().startswith(banner.strip())

@raises(HydeException)
def test_exception_raised_for_invalid_module():
    load_python_object("junk.junk.junk")
    assert False

@raises(HydeException)
def test_exception_raised_for_invalid_object():
    load_python_object("markdown.junk")
    assert False