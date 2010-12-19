# -*- coding: utf-8 -*-
"""
Use nose
`$ pip install nose`
`$ nosetests`
"""

from hyde.fs import FS, File, Folder
import codecs
import os
import shutil

from nose.tools import raises, with_setup, nottest

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

def test_exists():
    p = FS(__file__)
    assert p.exists
    p = FS(__file__ + "_some_junk")
    assert not p.exists
    f = FS(__file__).parent.parent
    assert f.exists
    f = FS(__file__).parent.child_folder('templates')
    assert f.exists

def test_create_folder():
    f = FS(__file__).parent
    assert f.exists
    f.make()
    assert True # No Exceptions
    c =  f.child_folder('__test__')
    assert not c.exists
    c.make()
    assert c.exists
    shutil.rmtree(str(c))
    assert not c.exists

def test_remove_folder():
    f = FS(__file__).parent
    c =  f.child_folder('__test__')
    assert not c.exists
    c.make()
    assert c.exists
    c.delete()
    assert not c.exists

def test_file_or_folder():
    f = FS.file_or_folder(__file__)
    assert isinstance(f, File)
    f = FS.file_or_folder(File(__file__).parent)
    assert isinstance(f, Folder)

DATA_ROOT = File(__file__).parent.child_folder('data')
TEMPLATE_ROOT = File(__file__).parent.child_folder('templates')
JINJA2 = TEMPLATE_ROOT.child_folder('jinja2')
HELPERS = File(JINJA2.child('helpers.html'))
INDEX = File(JINJA2.child('index.html'))
LAYOUT = File(JINJA2.child('layout.html'))

def test_ancestors():
    depth = 0
    next = JINJA2
    for folder in INDEX.ancestors():
        assert folder == next
        depth += 1
        next = folder.parent
    assert depth == len(JINJA2.path.split(os.sep))

def test_ancestors_stop():
    depth = 0
    next = JINJA2
    for folder in INDEX.ancestors(stop=TEMPLATE_ROOT.parent):
        print folder
        assert folder == next
        depth += 1
        next = folder.parent
    assert depth == 2

def test_fragment():
    print INDEX.get_fragment(TEMPLATE_ROOT)
    assert INDEX.get_fragment(TEMPLATE_ROOT) == Folder(JINJA2.name).child(INDEX.name)
    assert INDEX.get_fragment(TEMPLATE_ROOT.parent) == Folder(
                        TEMPLATE_ROOT.name).child_folder(JINJA2.name).child(INDEX.name)

def test_get_mirror():
    mirror = JINJA2.get_mirror(DATA_ROOT, source_root=TEMPLATE_ROOT)
    assert mirror == DATA_ROOT.child_folder(JINJA2.name)
    mirror = JINJA2.get_mirror(DATA_ROOT, source_root=TEMPLATE_ROOT.parent)
    assert mirror == DATA_ROOT.child_folder(TEMPLATE_ROOT.name).child_folder(JINJA2.name)

@nottest
def setup_data():
    DATA_ROOT.make()

@nottest
def cleanup_data():
    DATA_ROOT.delete()

@with_setup(setup_data, cleanup_data)
def test_copy_file():
    DATA_HELPERS = File(DATA_ROOT.child(HELPERS.name))
    assert not DATA_HELPERS.exists
    HELPERS.copy_to(DATA_ROOT)
    assert DATA_HELPERS.exists

@with_setup(setup_data, cleanup_data)
def test_copy_folder():
    assert DATA_ROOT.exists
    DATA_JINJA2 = DATA_ROOT.child_folder(JINJA2.name)
    assert not DATA_JINJA2.exists
    JINJA2.copy_to(DATA_ROOT)
    assert DATA_JINJA2.exists
    for f in [HELPERS, INDEX, LAYOUT]:
        assert File(DATA_JINJA2.child(f.name)).exists

@with_setup(setup_data, cleanup_data)
def test_copy_folder_target_missing():
    DATA_ROOT.delete()
    assert not DATA_ROOT.exists
    DATA_JINJA2 = DATA_ROOT.child_folder(JINJA2.name)
    assert not DATA_JINJA2.exists
    JINJA2.copy_to(DATA_ROOT)
    assert DATA_JINJA2.exists
    for f in [HELPERS, INDEX, LAYOUT]:
        assert File(DATA_JINJA2.child(f.name)).exists

@with_setup(setup_data, cleanup_data)
def test_copy_folder_contents():
    for f in [HELPERS, INDEX, LAYOUT]:
        assert not File(DATA_ROOT.child(f.name)).exists
    JINJA2.copy_contents_to(DATA_ROOT)
    for f in [HELPERS, INDEX, LAYOUT]:
        assert File(DATA_ROOT.child(f.name)).exists

@with_setup(setup_data, cleanup_data)
def test_read_all():
    utxt = u'åßcdeƒ'
    path = DATA_ROOT.child('unicode.txt')
    with codecs.open(path, 'w', 'utf-8') as f:
        f.write(utxt)

    txt = File(path).read_all()
    assert txt == utxt

@with_setup(setup_data, cleanup_data)
def test_write():
    utxt = u'åßcdeƒ'
    path = DATA_ROOT.child('unicode.txt')
    File(path).write(utxt)
    txt = File(path).read_all()
    assert txt == utxt

def test_walker():
    folders = []
    files = []
    complete = []

    with TEMPLATE_ROOT.walk() as walker:

        @walker.folder_visitor
        def visit_folder(f):
            folders.append(f)

        @walker.file_visitor
        def visit_file(f):
            files.append(f)

        @walker.finalizer
        def visit_complete():
            assert folders[0] == TEMPLATE_ROOT
            assert folders[1] == JINJA2
            assert INDEX in files
            assert HELPERS in files
            assert LAYOUT in files
            complete.append(True)

    assert len(files) == 4
    assert len(folders) == 2
    assert len(complete) == 1

def test_walker_templates_just_root():
    folders = []
    files = []
    complete = []

    with TEMPLATE_ROOT.walk() as walker:

        @walker.folder_visitor
        def visit_folder(f):
            assert f == TEMPLATE_ROOT
            folders.append(f)
            return False

        @walker.file_visitor
        def visit_file(f):
            files.append(f)

        @walker.finalizer
        def visit_complete():
            complete.append(True)

    assert len(files) == 0
    assert len(folders) == 1
    assert len(complete) == 1

def test_lister_templates():
    folders = []
    files = []
    complete = []

    with TEMPLATE_ROOT.list() as lister:

        @lister.folder_visitor
        def visit_folder(f):
            assert f == JINJA2
            folders.append(f)

        @lister.file_visitor
        def visit_file(f):
            files.append(f)

        @lister.finalizer
        def visit_complete():
            complete.append(True)

    assert len(files) == 0
    assert len(folders) == 1
    assert len(complete) == 1


def test_lister_jinja2():
    folders = []
    files = []
    complete = []

    with JINJA2.list() as lister:

        @lister.folder_visitor
        def visit_folder(f):
            folders.append(f)

        @lister.file_visitor
        def visit_file(f):
            files.append(f)

        @lister.finalizer
        def visit_complete():
            assert INDEX in files
            assert HELPERS in files
            assert LAYOUT in files
            complete.append(True)

    assert len(files) == 4
    assert len(folders) == 0
    assert len(complete) == 1