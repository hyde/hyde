# -*- coding: utf-8 -*-
"""
Use nose
`$ pip install nose`
`$ nosetests`
"""
import yaml

from hyde.fs import File, Folder
from hyde.model import Config, Expando
from hyde.site import Node, RootNode, Site

from nose.tools import raises, with_setup, nottest

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

def test_load():
    s = Site(TEST_SITE_ROOT)
    s.load()
    path = 'blog/2010/december'
    node = s.content.node_from_relative_path(path)
    assert node
    assert Folder(node.relative_path) == Folder(path)
    path += '/merry-christmas.html'
    resource = s.content.resource_from_relative_path(path)
    assert resource
    assert resource.relative_path == path
    assert not s.content.resource_from_relative_path('/happy-festivus.html')

def test_walk_resources():
    s = Site(TEST_SITE_ROOT)
    s.load()
    pages = [page.name for page in s.content.walk_resources()]
    expected = ["404.html",
                "about.html",
                "apple-touch-icon.png",
                "merry-christmas.html",
                "crossdomain.xml",
                "favicon.ico",
                "robots.txt"
                ]
    pages.sort()
    expected.sort()
    assert pages == expected


class TestSiteWithConfig(object):

    @classmethod
    def setup_class(cls):
        cls.SITE_PATH =  File(__file__).parent.child_folder('sites/test_jinja_with_config')
        cls.SITE_PATH.make()
        TEST_SITE_ROOT.copy_contents_to(cls.SITE_PATH)
        cls.config_file = File(cls.SITE_PATH.child('alternate.yaml'))
        with open(cls.config_file.path) as config:
            cls.config = Config(sitepath=cls.SITE_PATH, config_dict=yaml.load(config))
        cls.SITE_PATH.child_folder('content').rename_to(cls.config.content_root)

    @classmethod
    def teardown_class(cls):
        cls.SITE_PATH.delete()

    def test_load_with_config(self):
        s = Site(self.SITE_PATH, config = self.config)
        s.load()
        path = 'blog/2010/december'
        node = s.content.node_from_relative_path(path)
        assert node
        assert Folder(node.relative_path) == Folder(path)
        path += '/merry-christmas.html'
        resource = s.content.resource_from_relative_path(path)
        assert resource
        assert resource.relative_path == path
        assert not s.content.resource_from_relative_path('/happy-festivus.html')