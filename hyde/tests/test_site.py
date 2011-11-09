# -*- coding: utf-8 -*-
"""
Use nose
`$ pip install nose`
`$ nosetests`
"""
import yaml
from urllib import quote

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

def test_node_url():
    s = Site(TEST_SITE_ROOT)
    r = RootNode(TEST_SITE_ROOT.child_folder('content'), s)
    assert not r.module
    n = r.add_node(TEST_SITE_ROOT.child_folder('content/blog'))
    assert n.url == '/' + n.relative_path
    assert n.url == '/blog'
    c = r.add_node(TEST_SITE_ROOT.child_folder('content/blog/2010/december'))
    assert c.url == '/' + c.relative_path
    assert c.url == '/blog/2010/december'

def test_node_full_url():
    s = Site(TEST_SITE_ROOT)
    s.config.base_url = 'http://localhost'
    r = RootNode(TEST_SITE_ROOT.child_folder('content'), s)
    assert not r.module
    n = r.add_node(TEST_SITE_ROOT.child_folder('content/blog'))
    assert n.full_url == quote('http://localhost/blog')
    c = r.add_node(TEST_SITE_ROOT.child_folder('content/blog/2010/december'))
    assert c.full_url == quote('http://localhost/blog/2010/december')

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
                "robots.txt",
                "site.css"
                ]
    pages.sort()
    expected.sort()
    assert pages == expected

def test_contains_resource():
    s = Site(TEST_SITE_ROOT)
    s.load()
    path = 'blog/2010/december'
    node = s.content.node_from_relative_path(path)
    assert node.contains_resource('merry-christmas.html')

def test_get_resource():
    s = Site(TEST_SITE_ROOT)
    s.load()
    path = 'blog/2010/december'
    node = s.content.node_from_relative_path(path)
    resource = node.get_resource('merry-christmas.html')
    assert resource == s.content.resource_from_relative_path(Folder(path).child('merry-christmas.html'))

def test_resource_slug():
    s = Site(TEST_SITE_ROOT)
    s.load()
    path = 'blog/2010/december'
    node = s.content.node_from_relative_path(path)
    resource = node.get_resource('merry-christmas.html')
    assert resource.slug == 'merry-christmas'


def test_get_resource_from_relative_deploy_path():
    s = Site(TEST_SITE_ROOT)
    s.load()
    path = 'blog/2010/december'
    node = s.content.node_from_relative_path(path)
    resource = node.get_resource('merry-christmas.html')
    assert resource == s.content.resource_from_relative_deploy_path(Folder(path).child('merry-christmas.html'))
    resource.relative_deploy_path = Folder(path).child('merry-christmas.php')
    assert resource == s.content.resource_from_relative_deploy_path(Folder(path).child('merry-christmas.php'))

def test_is_processable_default_true():
    s = Site(TEST_SITE_ROOT)
    s.load()
    for page in s.content.walk_resources():
        assert page.is_processable

def test_relative_deploy_path():
    s = Site(TEST_SITE_ROOT)
    s.load()
    for page in s.content.walk_resources():
        assert page.relative_deploy_path == Folder(page.relative_path)
        assert page.url == page.relative_deploy_path

def test_relative_deploy_path_override():
    s = Site(TEST_SITE_ROOT)
    s.load()
    res = s.content.resource_from_relative_path('blog/2010/december/merry-christmas.html')
    res.relative_deploy_path = 'blog/2010/december/happy-holidays.html'
    for page in s.content.walk_resources():
        if res.source_file == page.source_file:
            assert page.relative_deploy_path == 'blog/2010/december/happy-holidays.html'
        else:
            assert page.relative_deploy_path == Folder(page.relative_path)

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
        s = Site(self.SITE_PATH, config=self.config)
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

    def test_content_url(self):
        s = Site(self.SITE_PATH, config=self.config)
        s.load()
        path = 'blog/2010/december'
        assert s.content_url(path) == "/" + path

    def test_media_url(self):
        s = Site(self.SITE_PATH, config=self.config)
        s.load()
        path = 'css/site.css'
        assert s.media_url(path) == "/media/" + path

    def test_is_media(self):
        s = Site(self.SITE_PATH, config=self.config)
        s.load()
        assert s.is_media('media/css/site.css')

        s.config.media_root = 'monkey'
        assert not s.is_media('media/css/site.css')
        assert s.is_media('monkey/css/site.css')

    def test_full_url_for_content(self):
        s = Site(self.SITE_PATH, config=self.config)
        s.load()
        path = 'blog/2010/december'
        assert s.full_url(path) == "/" + path

    def test_full_url_for_media(self):
        s = Site(self.SITE_PATH, config=self.config)
        s.load()
        path = 'media/css/site.css'
        assert s.is_media(path)
        full_url = s.full_url(path)
        assert full_url == "/" + path

    def test_media_url_from_resource(self):
        s = Site(self.SITE_PATH, config=self.config)
        s.load()
        path = 'css/site.css'
        resource = s.content.resource_from_relative_path(
                        Folder("media").child(path))
        assert resource
        assert resource.full_url == "/media/" + path

    def test_config_ignore(self):
        c = Config(self.SITE_PATH, config_dict=self.config.to_dict())
        s = Site(self.SITE_PATH, config=c)
        s.load()
        path = 'apple-touch-icon.png'
        resource = s.content.resource_from_relative_path(path)
        assert resource
        assert resource.full_url ==  "/" + path
        s = Site(self.SITE_PATH, config=c)
        s.config.ignore.append('*.png')
        resource = s.content.resource_from_relative_path(path)
        assert not resource

    def test_config_ignore_nodes(self):
        c = Config(self.SITE_PATH, config_dict=self.config.to_dict())
        git = self.SITE_PATH.child_folder('.git')
        git.make()
        s = Site(self.SITE_PATH, config=c)
        s.load()
        git_node = s.content.node_from_relative_path('.git')
        assert not git_node
        blog_node = s.content.node_from_relative_path('blog')
        assert blog_node
        assert blog_node.full_url ==  "/blog"
        s = Site(self.SITE_PATH, config=c)
        s.config.ignore.append('blog')
        blog_node = s.content.node_from_relative_path('blog')
        assert not blog_node
        git_node = s.content.node_from_relative_path('.git')
        assert not git_node
