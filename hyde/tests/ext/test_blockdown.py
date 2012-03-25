# -*- coding: utf-8 -*-
"""
Use nose
`$ pip install nose`
`$ nosetests`
"""
from hyde.generator import Generator
from hyde.site import Site

from fswrap import File
from pyquery import PyQuery

TEST_SITE = File(__file__).parent.parent.child_folder('_test')


class TestBlockdown(object):

    def setUp(self):
        TEST_SITE.make()
        TEST_SITE.parent.child_folder(
                    'sites/test_jinja').copy_contents_to(TEST_SITE)

    def tearDown(self):
        TEST_SITE.delete()

    def test_can_parse_blockdown(self):
        s = Site(TEST_SITE)
        s.config.plugins = ['hyde.ext.plugins.text.BlockdownPlugin']
        txt ="This template tests to make sure blocks can be replaced with markdownish syntax."
        templ = """
{%% extends "base.html" %%}
=====title========
%s
====/title========"""

        content = (templ.strip() % txt).strip()
        bd = File(TEST_SITE.child('content/blockdown.html'))
        bd.write(content)
        gen = Generator(s)
        gen.generate_resource_at_path(bd.path)
        res = s.content.resource_from_path(bd.path)
        target = File(s.config.deploy_root_path.child(res.relative_deploy_path))
        assert target.exists
        text = target.read_all()
        q = PyQuery(text)
        assert q('title').text().strip() == txt.strip()
