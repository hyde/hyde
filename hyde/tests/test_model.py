# -*- coding: utf-8 -*-
"""
Use nose
`$ pip install nose`
`$ nosetests`
"""
from hyde.model import Config, Expando

from fswrap import File, Folder

def test_expando_one_level():
    d = {"a": 123, "b": "abc"}
    x = Expando(d)
    assert x.a == d['a']
    assert x.b == d['b']

def test_expando_two_levels():
    d = {"a": 123, "b": {"c": 456}}
    x = Expando(d)
    assert x.a == d['a']
    assert x.b.c == d['b']['c']

def test_expando_three_levels():
    d = {"a": 123, "b": {"c": 456, "d": {"e": "abc"}}}
    x = Expando(d)
    assert x.a == d['a']
    assert x.b.c == d['b']['c']
    assert x.b.d.e == d['b']['d']['e']

def test_expando_update():
    d1 = {"a": 123, "b": "abc"}
    x = Expando(d1)
    assert x.a == d1['a']
    assert x.b == d1['b']
    d = {"b": {"c": 456, "d": {"e": "abc"}}, "f": "lmn"}
    x.update(d)
    assert  x.a == d1['a']
    assert x.b.c == d['b']['c']
    assert x.b.d.e == d['b']['d']['e']
    assert x.f == d["f"]
    d2 = {"a": 789, "f": "opq"}
    y = Expando(d2)
    x.update(y)
    assert x.a == 789
    assert x.f == "opq"

def test_expando_to_dict():
    d = {"a": 123, "b": {"c": 456, "d": {"e": "abc"}}}
    x = Expando(d)
    assert d == x.to_dict()

def test_expando_to_dict_with_update():
    d1 = {"a": 123, "b": "abc"}
    x = Expando(d1)
    d = {"b": {"c": 456, "d": {"e": "abc"}}, "f": "lmn"}
    x.update(d)
    expected = {}
    expected.update(d1)
    expected.update(d)
    assert expected == x.to_dict()
    d2 = {"a": 789, "f": "opq"}
    y = Expando(d2)
    x.update(y)
    expected.update(d2)
    assert expected == x.to_dict()

TEST_SITE = File(__file__).parent.child_folder('_test')

import yaml
class TestConfig(object):

    @classmethod
    def setup_class(cls):
        cls.conf1 = """
        mode: development
        content_root: stuff # Relative path from site root
        media_root: media # Relative path from site root
        media_url: /media
        widgets:
        plugins:
        aggregators:
        """

        cls.conf2 = """
        mode: development
        deploy_root: ~/deploy_site
        content_root: site/stuff # Relative path from site root
        media_root: mmm # Relative path from site root
        media_url: /media
        widgets:
        plugins:
        aggregators:
        """

    def setUp(self):
        TEST_SITE.make()
        TEST_SITE.parent.child_folder('sites/test_jinja').copy_contents_to(TEST_SITE)

    def tearDown(self):
        TEST_SITE.delete()

    def test_default_configuration(self):
        c = Config(sitepath=TEST_SITE, config_dict={})
        for root in ['content', 'layout']:
            name = root + '_root'
            path = name + '_path'
            assert hasattr(c, name)
            assert getattr(c, name) == root
            assert hasattr(c, path)
            assert getattr(c, path) == TEST_SITE.child_folder(root)
        assert c.media_root_path == c.content_root_path.child_folder('media')
        assert hasattr(c, 'plugins')
        assert len(c.plugins) == 0
        assert hasattr(c, 'ignore')
        assert c.ignore == ["*~", "*.bak", ".hg", ".git", ".svn"]
        assert c.deploy_root_path == TEST_SITE.child_folder('deploy')
        assert c.not_found == '404.html'
        assert c.meta.nodemeta == 'meta.yaml'

    def test_conf1(self):
        c = Config(sitepath=TEST_SITE, config_dict=yaml.load(self.conf1))
        assert c.content_root_path == TEST_SITE.child_folder('stuff')

    def test_conf2(self):
        c = Config(sitepath=TEST_SITE, config_dict=yaml.load(self.conf2))
        assert c.content_root_path == TEST_SITE.child_folder('site/stuff')
        assert c.media_root_path == c.content_root_path.child_folder('mmm')
        assert c.media_url == TEST_SITE.child_folder('/media')
        assert c.deploy_root_path == Folder('~/deploy_site')

    def test_read_from_file_by_default(self):
        File(TEST_SITE.child('site.yaml')).write(self.conf2)
        c = Config(sitepath=TEST_SITE)
        assert c.content_root_path == TEST_SITE.child_folder('site/stuff')
        assert c.media_root_path == c.content_root_path.child_folder('mmm')
        assert c.media_url == TEST_SITE.child_folder('/media')
        assert c.deploy_root_path == Folder('~/deploy_site')

    def test_read_from_specified_file(self):
        File(TEST_SITE.child('another.yaml')).write(self.conf2)
        c = Config(sitepath=TEST_SITE, config_file='another.yaml')
        assert c.content_root_path == TEST_SITE.child_folder('site/stuff')
        assert c.media_root_path == c.content_root_path.child_folder('mmm')
        assert c.media_url == TEST_SITE.child_folder('/media')
        assert c.deploy_root_path == Folder('~/deploy_site')

    def test_extends(self):
        another = """
        extends: site.yaml
        mode: production
        media_root: xxx
        """
        File(TEST_SITE.child('site.yaml')).write(self.conf2)
        File(TEST_SITE.child('another.yaml')).write(another)
        c = Config(sitepath=TEST_SITE, config_file='another.yaml')
        assert c.mode == 'production'
        assert c.content_root_path == TEST_SITE.child_folder('site/stuff')
        assert c.media_root_path == c.content_root_path.child_folder('xxx')
        assert c.media_url == TEST_SITE.child_folder('/media')
        assert c.deploy_root_path == Folder('~/deploy_site')
