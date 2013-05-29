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

DRAFT_POST = """

---
is_draft: true
---

A draft post.

"""

class TestDrafts(object):

    def setUp(self):
        TEST_SITE.make()
        TEST_SITE.parent.child_folder(
                    'sites/test_jinja').copy_contents_to(TEST_SITE)
        draft = TEST_SITE.child_file('content/blog/2013/may/draft-post.html')
        draft.parent.make()
        draft.write(DRAFT_POST)

    def tearDown(self):
        TEST_SITE.delete()

    def test_drafts_are_skipped_in_production(self):
        s = Site(TEST_SITE)
        cfg = """
        mode: production
        plugins:
            - hyde.ext.plugins.meta.MetaPlugin
            - hyde.ext.plugins.blog.DraftsPlugin
        """
        import yaml
        s.config = Config(TEST_SITE, config_dict=yaml.load(cfg))
        s.load()
        gen = Generator(s)
        gen.generate_all()
        assert not s.config.deploy_root_path.child_file(
                    'blog/2013/may/draft-post.html').exists

    def test_drafts_are_published_in_development(self):
        s = Site(TEST_SITE)
        cfg = """
        mode: development
        plugins:
            - hyde.ext.plugins.meta.MetaPlugin
            - hyde.ext.plugins.blog.DraftsPlugin
        """
        import yaml
        s.config = Config(TEST_SITE, config_dict=yaml.load(cfg))
        s.load()
        gen = Generator(s)
        gen.generate_all()
        assert s.config.deploy_root_path.child_file(
                    'blog/2013/may/draft-post.html').exists


