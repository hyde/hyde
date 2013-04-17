# -*- coding: utf-8 -*-
"""
Use nose
`$ pip install nose`
`$ nosetests`
"""
from hyde.generator import Generator
from hyde.site import Site

from fswrap import File, Folder
from pyquery import PyQuery
import yaml


TEST_SITE = File(__file__).parent.parent.child_folder('_test')


class TestMeta(object):

    def setUp(self):
        TEST_SITE.make()
        TEST_SITE.parent.child_folder(
                    'sites/test_jinja').copy_contents_to(TEST_SITE)

    def tearDown(self):
        TEST_SITE.delete()

    def test_can_set_standard_attributes(self):
        text = """
---
is_processable: False
---
{% extends "base.html" %}
"""
        about2 = File(TEST_SITE.child('content/about2.html'))
        about2.write(text)
        s = Site(TEST_SITE)
        s.load()
        res = s.content.resource_from_path(about2.path)
        assert res.is_processable

        s.config.plugins = ['hyde.ext.plugins.meta.MetaPlugin']
        gen = Generator(s)
        gen.generate_all()
        assert not res.meta.is_processable
        assert not res.is_processable

    def test_ignores_pattern_in_content(self):
        text = """
{% markdown %}

Heading 1
===

Heading 2
===

{% endmarkdown %}
"""
        about2 = File(TEST_SITE.child('content/about2.html'))
        about2.write(text)
        s = Site(TEST_SITE)
        s.load()
        res = s.content.resource_from_path(about2.path)
        assert res.is_processable

        s.config.plugins = ['hyde.ext.plugins.meta.MetaPlugin']
        gen = Generator(s)
        gen.generate_all()
        target = File(Folder(s.config.deploy_root_path).child('about2.html'))
        text = target.read_all()
        q = PyQuery(text)
        assert q("h1").length == 2
        assert q("h1:nth-child(1)").text().strip() == "Heading 1"
        assert q("h1:nth-child(2)").text().strip() == "Heading 2"

    def test_can_load_front_matter(self):
        d = {'title': 'A nice title',
            'author': 'Lakshmi Vyas',
            'twitter': 'lakshmivyas'}
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

    def test_can_load_from_node_meta(self):
        d = {'title': 'A nice title',
            'author': 'Lakshmi Vyas',
            'twitter': 'lakshmivyas'}
        text = """
===
title: Even nicer title
===
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
        meta = File(TEST_SITE.child('content/meta.yaml'))
        meta.write(yaml.dump(d))
        s = Site(TEST_SITE)
        s.config.plugins = ['hyde.ext.plugins.meta.MetaPlugin']
        gen = Generator(s)
        gen.generate_all()
        res = s.content.resource_from_path(about2.path)
        assert hasattr(res, 'meta')
        assert hasattr(res.meta, 'title')
        assert hasattr(res.meta, 'author')
        assert hasattr(res.meta, 'twitter')
        assert res.meta.title == "Even nicer title"
        assert res.meta.author == "Lakshmi Vyas"
        assert res.meta.twitter == "lakshmivyas"
        target = File(Folder(s.config.deploy_root_path).child('about2.html'))
        text = target.read_all()
        q = PyQuery(text)
        for k, v in d.items():
            if not k == 'title':
                assert v in q("span." + k).text()
        assert q("span.title").text() == "Even nicer title"

    def test_can_load_from_site_meta(self):
        d = {'title': 'A nice title',
            'author': 'Lakshmi Vyas'}
        text = """
---
title: Even nicer title
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
        meta = File(TEST_SITE.child('content/nodemeta.yaml'))
        meta.write(yaml.dump(d))
        s = Site(TEST_SITE)
        s.config.plugins = ['hyde.ext.plugins.meta.MetaPlugin']
        s.config.meta = {
            'author': 'Lakshmi',
            'twitter': 'lakshmivyas'
        }
        gen = Generator(s)
        gen.generate_all()
        res = s.content.resource_from_path(about2.path)
        assert hasattr(res, 'meta')
        assert hasattr(res.meta, 'title')
        assert hasattr(res.meta, 'author')
        assert hasattr(res.meta, 'twitter')
        assert res.meta.title == "Even nicer title"
        assert res.meta.author == "Lakshmi Vyas"
        assert res.meta.twitter == "lakshmivyas"
        target = File(Folder(s.config.deploy_root_path).child('about2.html'))
        text = target.read_all()
        q = PyQuery(text)
        for k, v in d.items():
            if not k == 'title':
                assert v in q("span." + k).text()
        assert q("span.title").text() == "Even nicer title"


    def test_multiple_levels(self):

        page_d = {'title': 'An even nicer title'}

        blog_d = {'author': 'Laks'}

        content_d  = {'title': 'A nice title',
                      'author': 'Lakshmi Vyas'}

        site_d = {'author': 'Lakshmi',
                  'twitter': 'lakshmivyas',
                  'nodemeta': 'meta.yaml'}
        text = """
---
title: %(title)s
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
        about2 = File(TEST_SITE.child('content/blog/about2.html'))
        about2.write(text % page_d)
        content_meta = File(TEST_SITE.child('content/nodemeta.yaml'))
        content_meta.write(yaml.dump(content_d))
        content_meta = File(TEST_SITE.child('content/blog/meta.yaml'))
        content_meta.write(yaml.dump(blog_d))
        s = Site(TEST_SITE)
        s.config.plugins = ['hyde.ext.plugins.meta.MetaPlugin']
        s.config.meta = site_d
        gen = Generator(s)
        gen.generate_all()
        expected = {}

        expected.update(site_d)
        expected.update(content_d)
        expected.update(blog_d)
        expected.update(page_d)

        res = s.content.resource_from_path(about2.path)
        assert hasattr(res, 'meta')
        for k, v in expected.items():
            assert hasattr(res.meta, k)
            assert getattr(res.meta, k) == v
        target = File(Folder(s.config.deploy_root_path).child('blog/about2.html'))
        text = target.read_all()
        q = PyQuery(text)
        for k, v in expected.items():
            if k != 'nodemeta':
                assert v in q("span." + k).text()
