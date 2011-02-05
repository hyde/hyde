# -*- coding: utf-8 -*-
"""
Use nose
`$ pip install nose`
`$ nosetests`
"""
from hyde.fs import File, Folder
from hyde.generator import Generator
from hyde.site import Site

from pyquery import PyQuery

from nose.tools import nottest

TEST_SITE = File(__file__).parent.parent.child_folder('_test')


class TestDepends(object):

    def setUp(self):
        TEST_SITE.make()
        TEST_SITE.parent.child_folder(
                    'sites/test_jinja').copy_contents_to(TEST_SITE)

    def tearDown(self):
        TEST_SITE.delete()

    def test_depends(self):
        s = Site(TEST_SITE)
        s.config.plugins = ['hyde.ext.plugins.meta.MetaPlugin',
                            'hyde.ext.plugins.depends.DependsPlugin']
        text = """
===
depends: index.html
===
{% set ind = 'index.html' %}
{% refer to ind as index %}
"""
        inc = File(TEST_SITE.child('content/inc.md'))
        inc.write(text)
        gen = Generator(s)
        gen.load_site_if_needed()
        gen.load_template_if_needed()
        res = s.content.resource_from_relative_path('inc.md')
        deps = list(gen.get_dependencies(res))

        assert len(deps) == 3

        assert 'helpers.html' in deps
        assert 'layout.html' in deps
        assert 'index.html' in deps