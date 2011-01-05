# -*- coding: utf-8 -*-
"""
Use nose
`$ pip install nose`
`$ nosetests`
"""
from hyde.model import Config, Expando
from hyde.fs import *

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

TEST_SITE_ROOT = File(__file__).parent.child_folder('sites/test_jinja')
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

    def test_default_configuration(self):
        c = Config(sitepath=TEST_SITE_ROOT)
        for root in ['content', 'layout', 'media']:
            name = root + '_root'
            path = name + '_path'
            assert hasattr(c, name)
            assert getattr(c, name) == root
            assert hasattr(c, path)
            assert getattr(c, path) == TEST_SITE_ROOT.child_folder(root)
        assert hasattr(c, 'plugins')
        assert len(c.plugins) == 0
        assert c.deploy_root_path == TEST_SITE_ROOT.child_folder('deploy')
        assert c.not_found == '404.html'

    def test_conf1(self):
        c = Config(sitepath=TEST_SITE_ROOT, config_dict=yaml.load(self.conf1))
        assert c.content_root_path == TEST_SITE_ROOT.child_folder('stuff')

    def test_conf2(self):
        c = Config(sitepath=TEST_SITE_ROOT, config_dict=yaml.load(self.conf2))
        assert c.content_root_path == TEST_SITE_ROOT.child_folder('site/stuff')
        assert c.media_root_path == TEST_SITE_ROOT.child_folder('mmm')
        assert c.media_url == TEST_SITE_ROOT.child_folder('/media')
        assert c.deploy_root_path == Folder('~/deploy_site')