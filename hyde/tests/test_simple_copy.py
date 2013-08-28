# -*- coding: utf-8 -*-
"""
Tests the simple copy feature.

In order to mark some files to simply be copied to the
destination without any processing what so ever add this
to the config (site.yaml for example):
simple_copy:
    - media/css/*.css
    - media/js/*.js
    - **/*.js

Matching is done with `fnmatch` module. So any `glob` that fnmatch
can process is a valid pattern.

Use nose
`$ pip install nose`
`$ nosetests`
"""
import yaml

from hyde.model import Config
from hyde.site import Site
from hyde.generator import Generator

from fswrap import File
from nose.tools import nottest


TEST_SITE_ROOT = File(__file__).parent.child_folder('sites/test_jinja')

class TestSimpleCopy(object):
    @classmethod
    def setup_class(cls):
        cls.SITE_PATH =  File(__file__).parent.child_folder('sites/test_jinja_with_config')
        cls.SITE_PATH.make()
        TEST_SITE_ROOT.copy_contents_to(cls.SITE_PATH)

    @classmethod
    def teardown_class(cls):
        cls.SITE_PATH.delete()

    @nottest
    def setup_config(self, passthru):
        self.config_file = File(self.SITE_PATH.child('site.yaml'))
        with open(self.config_file.path) as config:
            conf = yaml.load(config)
            conf['simple_copy'] = passthru
            self.config = Config(sitepath=self.SITE_PATH, config_dict=conf)

    def test_simple_copy_basic(self):
        self.setup_config([
            'about.html'
        ])
        s = Site(self.SITE_PATH, config=self.config)
        s.load()
        res = s.content.resource_from_relative_path('about.html')
        assert res
        assert res.simple_copy

    def test_simple_copy_directory(self):
        self.setup_config([
            '**/*.html'
        ])
        s = Site(self.SITE_PATH, config=self.config)
        s.load()
        res = s.content.resource_from_relative_path('about.html')
        assert res
        assert not res.simple_copy
        res = s.content.resource_from_relative_path('blog/2010/december/merry-christmas.html')
        assert res
        assert res.simple_copy

    def test_simple_copy_multiple(self):
        self.setup_config([
            '**/*.html',
            'media/css/*.css'
        ])
        s = Site(self.SITE_PATH, config=self.config)
        s.load()
        res = s.content.resource_from_relative_path('about.html')
        assert res
        assert not res.simple_copy
        res = s.content.resource_from_relative_path('blog/2010/december/merry-christmas.html')
        assert res
        assert res.simple_copy
        res = s.content.resource_from_relative_path('media/css/site.css')
        assert res
        assert res.simple_copy

    def test_generator(self):
        self.setup_config([
            '**/*.html',
            'media/css/*.css'
        ])
        s = Site(self.SITE_PATH, self.config)
        g = Generator(s)
        g.generate_all()
        source = s.content.resource_from_relative_path('blog/2010/december/merry-christmas.html')
        target = File(s.config.deploy_root_path.child(source.relative_deploy_path))
        left = source.source_file.read_all()
        right = target.read_all()
        assert left == right

    def test_plugins(self):

        text = """
---
title: Hey
author: Me
twitter: @me
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
        index = File(self.SITE_PATH.child('content/blog/index.html'))
        index.write(text)
        self.setup_config([
            '**/*.html',
            'media/css/*.css'
        ])
        conf = {'plugins': ['hyde.ext.plugins.meta.MetaPlugin']}
        conf.update(self.config.to_dict())
        s = Site(self.SITE_PATH, Config(sitepath=self.SITE_PATH, config_dict=conf))
        g = Generator(s)
        g.generate_all()
        source = s.content.resource_from_relative_path('blog/index.html')
        target = File(s.config.deploy_root_path.child(source.relative_deploy_path))
        left = source.source_file.read_all()
        right = target.read_all()
        assert left == right