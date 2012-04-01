# -*- coding: utf-8 -*-
"""
Use nose
`$ pip install nose`
`$ nosetests`
"""

from hyde.generator import Generator
from hyde.site import Site
from hyde.model import Config

from fswrap import File

TEST_SITE = File(__file__).parent.parent.child_folder('_test')


class TestFlattner(object):

    def setUp(self):
        TEST_SITE.make()
        TEST_SITE.parent.child_folder(
                    'sites/test_jinja').copy_contents_to(TEST_SITE)

    def tearDown(self):
        TEST_SITE.delete()

    def test_can_flatten(self):
        s = Site(TEST_SITE)
        cfg = """
        plugins:
            - hyde.ext.plugins.structure.FlattenerPlugin
        flattener:
            items:
                -
                    source: blog
                    target: ''
        """
        import yaml
        s.config = Config(TEST_SITE, config_dict=yaml.load(cfg))
        s.load()
        gen = Generator(s)
        gen.generate_all()

        assert not s.config.deploy_root_path.child_folder('blog').exists
        assert File(s.config.deploy_root_path.child('merry-christmas.html')).exists

    def test_flattener_fixes_nodes(self):
        s = Site(TEST_SITE)
        cfg = """
        plugins:
            - hyde.ext.plugins.structure.FlattenerPlugin
        flattener:
            items:
                -
                    source: blog
                    target: ''
        """
        import yaml
        s.config = Config(TEST_SITE, config_dict=yaml.load(cfg))
        s.load()
        gen = Generator(s)
        gen.generate_all()
        blog_node = s.content.node_from_relative_path('blog')

        assert blog_node
        assert blog_node.url == '/'


