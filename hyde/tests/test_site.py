# -*- coding: utf-8 -*-
"""
Use nose
`$ pip install nose`
`$ nosetests`
"""
from hyde.fs import File, Folder
from hyde.site import Node, RootNode, Site


TEST_SITE_ROOT = File(__file__).parent.child_folder('sites/test_jinja')

def test_node_site():
    s = Site(TEST_SITE_ROOT)
    r = RootNode(TEST_SITE_ROOT.child_folder('content'), s)
    assert r.site == s
    n = Node(r.source_folder.child_folder('blog'), r)
    assert n.site == s

def test_node_root():
    s = Site(TEST_SITE_ROOT)
    r = RootNode(TEST_SITE_ROOT.child_folder('content'), s)
    assert r.root == r
    n = Node(r.source_folder.child_folder('blog'), r)
    assert n.root == r

def test_node_parent():
    s = Site(TEST_SITE_ROOT)
    r = RootNode(TEST_SITE_ROOT.child_folder('content'), s)
    c = r.add_node(TEST_SITE_ROOT.child_folder('content/blog/2010/december'))
    assert c.parent == r.node_from_relative_path('blog/2010')

def test_node_module():
    s = Site(TEST_SITE_ROOT)
    r = RootNode(TEST_SITE_ROOT.child_folder('content'), s)
    assert not r.module
    n = r.add_node(TEST_SITE_ROOT.child_folder('content/blog'))
    assert n.module == n
    c = r.add_node(TEST_SITE_ROOT.child_folder('content/blog/2010/december'))
    assert c.module == n

def test_node_relative_path():
    s = Site(TEST_SITE_ROOT)
    r = RootNode(TEST_SITE_ROOT.child_folder('content'), s)
    assert not r.module
    n = r.add_node(TEST_SITE_ROOT.child_folder('content/blog'))
    assert n.relative_path == 'blog'
    c = r.add_node(TEST_SITE_ROOT.child_folder('content/blog/2010/december'))
    assert c.relative_path == 'blog/2010/december'

def test_build():
    s = Site(TEST_SITE_ROOT)
    s.build()
    path = 'blog/2010/december'
    node = s.content.node_from_relative_path(path)
    assert node
    assert Folder(node.relative_path) == Folder(path)
    path += '/merry-christmas.html'
    resource = s.content.resource_from_relative_path(path)
    assert resource
    assert resource.relative_path == path
    assert not s.content.resource_from_relative_path('/happy-festivus.html')
