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
    assert unicode(f) == __file__
    assert repr(f) == __file__

def test_name():
    f = FS(__file__)
    assert f.name == os.path.basename(__file__)

def test_equals():
    f = FS('/blog/2010/december')
    g = FS('/blog/2010/december')
    h = FS('/blog/2010/december/')
    i = FS('/blog/2010/november')
    assert f == f.path
    assert f == g
    assert f == h
    assert f != i

def test_name_without_extension():
    f = File(__file__)
    assert f.name_without_extension == "test_fs"

def test_extension():
    f = File(__file__)
    assert f.extension == os.path.splitext(__file__)[1]
    f = File("abc")
    assert f.extension == ''

def test_kind():
    f = File(__file__)
    assert f.kind == os.path.splitext(__file__)[1].lstrip('.')
    f = File("abc")
    assert f.kind == ''

def test_can_create_temp_file():
    text = "A for apple"
    f = File.make_temp(text)
    assert f.exists
    assert text == f.read_all()
    f.delete()
    assert not f.exists

def test_time_functions():
    f1 = File(__file__)
    t1 = f1.last_modified
    f2 = File.make_temp("I am new")
    t2  = f2.last_modified
    assert t1 < t2
    assert f2.has_changed_since(t1)
    assert f1.older_than(f2)


def test_path_expands_user():
    f = File("~/abc/def")
    assert f.path == os.path.expanduser("~/abc/def")

def test_fully_expanded_path():
    f = File(__file__).parent
    n = f.child_folder('../' + f.name)
    e = Folder(n.fully_expanded_path)
    assert n != e
    assert f == e

def test_parent():
    f = File(__file__)
    p = f.parent
    assert hasattr(p, 'child_folder')
    assert unicode(p) == os.path.dirname(__file__)

def test_child():
    p = File(__file__).parent
    c = p.child('data.dat')
    assert c == os.path.join(os.path.dirname(__file__), 'data.dat')

def test_child_folder():
    p = File(__file__).parent
    c = p.child_folder('data')
    assert hasattr(c, 'child_folder')
    assert unicode(c) == os.path.join(os.path.dirname(__file__), 'data')

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
    shutil.rmtree(unicode(c))
    assert not c.exists

def test_remove_folder():
    f = FS(__file__).parent
    c =  f.child_folder('__test__')
    assert not c.exists
    c.make()
    assert c.exists
    c.delete()
    assert not c.exists

def test_can_remove_file():
    f = FS(__file__).parent
    c =  f.child_folder('__test__')
    c.make()
    assert c.exists
    txt = "abc"
    abc = File(c.child('abc.txt'))
    abc.write(txt)
    assert abc.exists
    abc.delete()
    assert not abc.exists
    abc.delete()
    assert True # No Exception
    c.delete()

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
LOGO = File(TEMPLATE_ROOT.child('../../../resources/hyde-logo.png'))
XML = File(TEMPLATE_ROOT.child('../sites/test_jinja/content/crossdomain.xml'))

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
        assert folder == next
        depth += 1
        next = folder.parent
    assert depth == 2

def test_is_descendant_of():
    assert INDEX.is_descendant_of(JINJA2)
    assert JINJA2.is_descendant_of(TEMPLATE_ROOT)
    assert INDEX.is_descendant_of(TEMPLATE_ROOT)
    assert not INDEX.is_descendant_of(DATA_ROOT)

def test_get_relative_path():
    assert INDEX.get_relative_path(TEMPLATE_ROOT) == Folder(JINJA2.name).child(INDEX.name)
    assert INDEX.get_relative_path(TEMPLATE_ROOT.parent) == Folder(
                        TEMPLATE_ROOT.name).child_folder(JINJA2.name).child(INDEX.name)
    assert JINJA2.get_relative_path(JINJA2) == ""

def test_get_mirror():
    mirror = JINJA2.get_mirror(DATA_ROOT, source_root=TEMPLATE_ROOT)
    assert mirror == DATA_ROOT.child_folder(JINJA2.name)
    mirror = JINJA2.get_mirror(DATA_ROOT, source_root=TEMPLATE_ROOT.parent)
    assert mirror == DATA_ROOT.child_folder(TEMPLATE_ROOT.name).child_folder(JINJA2.name)

def test_mimetype():
    assert HELPERS.mimetype == 'text/html'
    assert LOGO.mimetype == 'image/png'

def test_is_text():
    assert HELPERS.is_text
    assert not LOGO.is_text
    assert XML.is_text

def test_is_image():
    assert not HELPERS.is_image
    assert LOGO.is_image

def test_file_size():
    assert LOGO.size == 1942

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
def test_move_folder():
    DATA_JUNK = DATA_ROOT.child_folder('junk')
    assert not DATA_JUNK.exists
    JINJA2.copy_contents_to(DATA_JUNK)
    assert DATA_JUNK.exists
    for f in [HELPERS, INDEX, LAYOUT]:
        assert File(DATA_JUNK.child(f.name)).exists
    DATA_JUNK2 = DATA_ROOT.child_folder('second_junk')
    assert not DATA_JUNK2.exists
    DATA_JUNK.move_to(DATA_JUNK2)
    assert not DATA_JUNK.exists
    assert DATA_JUNK2.exists
    for f in [HELPERS, INDEX, LAYOUT]:
        assert File(DATA_JUNK2.child_folder(
                    DATA_JUNK.name).child(
                        f.name)).exists

@with_setup(setup_data, cleanup_data)
def test_rename_folder():
    DATA_JUNK = DATA_ROOT.child_folder('junk')
    assert not DATA_JUNK.exists
    JINJA2.copy_contents_to(DATA_JUNK)
    for f in [HELPERS, INDEX, LAYOUT]:
        assert File(DATA_JUNK.child(f.name)).exists
    DATA_JUNK2 = DATA_ROOT.child_folder('junk2')
    assert DATA_JUNK.exists
    assert not DATA_JUNK2.exists
    DATA_JUNK.rename_to('junk2')
    assert not DATA_JUNK.exists
    assert DATA_JUNK2.exists
    for f in [HELPERS, INDEX, LAYOUT]:
        assert File(DATA_JUNK2.child(f.name)).exists

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

    with TEMPLATE_ROOT.walker as walker:

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

def test_walker_walk_all():
    items = list(TEMPLATE_ROOT.walker.walk_all())
    assert len(items) == 6
    assert TEMPLATE_ROOT in items
    assert JINJA2 in items
    assert INDEX in items
    assert HELPERS in items
    assert LAYOUT in items

def test_walker_walk_files():
    items = list(TEMPLATE_ROOT.walker.walk_files())
    assert len(items) == 4
    assert INDEX in items
    assert HELPERS in items
    assert LAYOUT in items

def test_walker_walk_folders():
    items = list(TEMPLATE_ROOT.walker.walk_folders())
    assert len(items) == 2
    assert TEMPLATE_ROOT in items
    assert JINJA2 in items

def test_walker_templates_just_root():
    folders = []
    files = []
    complete = []

    with TEMPLATE_ROOT.walker as walker:

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

    with TEMPLATE_ROOT.lister as lister:

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


def test_lister_list_all():
    items = list(TEMPLATE_ROOT.lister.list_all())
    assert len(items) == 1
    assert JINJA2 in items
    items = list(JINJA2.lister.list_all())
    assert len(items) == 4
    assert INDEX in items
    assert HELPERS in items
    assert LAYOUT in items


def test_lister_list_files():
    items = list(TEMPLATE_ROOT.lister.list_files())
    assert len(items) == 0
    items = list(JINJA2.lister.list_files())
    assert len(items) == 4
    assert INDEX in items
    assert HELPERS in items
    assert LAYOUT in items

def test_lister_list_folders():
    items = list(TEMPLATE_ROOT.lister.list_folders())
    assert len(items) == 1
    assert JINJA2 in items
    items = list(JINJA2.lister.list_folders())
    assert len(items) == 0

def test_lister_jinja2():
    folders = []
    files = []
    complete = []

    with JINJA2.lister as lister:

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