# -*- coding: utf-8 -*-
"""
Use nose
`$ pip install nose`
`$ nosetests`
"""
from hyde.ext.plugins.meta import MetaPlugin
from hyde.fs import File, Folder
from hyde.generator import Generator
from hyde.site import Site

from pyquery import PyQuery
import yaml


TEST_SITE = File(__file__).parent.parent.child_folder('_test')


class TestMeta(object):

    def setUp(self):
        TEST_SITE.make()
        TEST_SITE.parent.child_folder('sites/test_jinja').copy_contents_to(TEST_SITE)

    def tearDown(self):
        TEST_SITE.delete()


    def test_can_load_front_matter(self):
        d = {
            'title': 'A nice title',
            'author': 'Lakshmi Vyas',
            'twitter': 'lakshmivyas'
        }
        text = """
---
title: %(title)s
author: %(author)s
twitter: %(twitter)s
---
{%% extends "base.html" %%}

{%% block main %%}
    Hi!

    I am a test template to make sure jinja2 generation works well with hyde.
    <span class="title">{{resource.meta.title}}</span>
    <span class="author">{{resource.meta.author}}</span>
    <span class="twitter">{{resource.meta.twitter}}</span>
{%% endblock %%}
"""
        about2 = File(TEST_SITE.child('content/about2.html'))
        about2.write(text % d)
        s = Site(TEST_SITE)
        s.config.plugins = ['hyde.ext.plugins.meta.MetaPlugin']
        gen = Generator(s)
        gen.generate_all()
        res = s.content.resource_from_path(about2.path)

        assert hasattr(res, 'meta')
        assert hasattr(res.meta, 'title')
        assert hasattr(res.meta, 'author')
        assert hasattr(res.meta, 'twitter')
        assert res.meta.title == "A nice title"
        assert res.meta.author == "Lakshmi Vyas"
        assert res.meta.twitter == "lakshmivyas"
        target = File(Folder(s.config.deploy_root_path).child('about2.html'))
        text = target.read_all()
        q = PyQuery(text)
        for k, v in d.items():
            assert v in q("span." + k).text()