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

import yaml


TEST_SITE = File(__file__).parent.parent.child_folder('_test')


class TestMeta(object):

    def setUp(self):
        TEST_SITE.make()
        TEST_SITE.parent.child_folder('sites/test_jinja').copy_contents_to(TEST_SITE)

    def tearDown(self):
        TEST_SITE.delete()


    def test_can_load_front_matter(self):
        front_matter = """
---
title: A nice title
author: Lakshmi Vyas
twitter: lakshmivyas
---
"""
        about1 = File(TEST_SITE.child('content/about.html'))
        about2 = File(TEST_SITE.child('content/about2.html'))

        text = front_matter
        text += "\n"
        text += about1.read_all()

        about2.write(text)
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