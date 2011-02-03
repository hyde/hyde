# -*- coding: utf-8 -*-
"""
Use nose
`$ pip install nose`
`$ nosetests`
"""
from hyde.ext.plugins.meta import MetaPlugin
from hyde.ext.plugins.sorter import SorterPlugin
from hyde.ext.plugins.grouper import GrouperPlugin
from hyde.fs import File, Folder
from hyde.generator import Generator
from hyde.site import Site
from hyde.model import Config, Expando
import yaml

TEST_SITE = File(__file__).parent.parent.child_folder('_test')


class TestGrouperSingleLevel(object):

    def setUp(self):
        TEST_SITE.make()
        TEST_SITE.parent.child_folder(
                  'sites/test_grouper').copy_contents_to(TEST_SITE)

        self.s = Site(TEST_SITE)
        cfg = """
        nodemeta: meta.yaml
        plugins:
          - hyde.ext.meta.MetaPlugin
          - hyde.ext.sorter.SorterPlugin
          - hyde.ext.grouper.GrouperPlugin
        sorter:
          kind:
              attr:
                  - source_file.kind
              filters:
                  is_processable: True
        grouper:
          section:
              description: Sections in the site
              sorter: kind
              groups:
                  -
                      name: start
                      description: Getting Started
                  -
                      name: plugins
                      description: Plugins


        """
        self.s.config = Config(TEST_SITE, config_dict=yaml.load(cfg))
        self.s.load()
        MetaPlugin(self.s).begin_site()
        SorterPlugin(self.s).begin_site()
        GrouperPlugin(self.s).begin_site()

    def tearDown(self):
        TEST_SITE.delete()

    def test_site_grouper_groups(self):

        groups = dict([(g.name, g) for g in self.s.grouper['section'].groups])
        assert len(groups) == 2
        assert 'start' in groups
        assert 'plugins' in groups

    def test_site_grouper_walk_groups(self):

        groups = dict([(g.name, g) for g in self.s.grouper['section'].walk_groups()])
        assert len(groups) == 3
        assert 'section' in groups
        assert 'start' in groups
        assert 'plugins' in groups

    def test_walk_section_groups(self):

        assert hasattr(self.s.content, 'walk_section_groups')
        groups = dict([(g.name, g) for g in self.s.content.walk_section_groups()])
        assert len(groups) == 2
        assert 'start' in groups
        assert 'plugins' in groups

    def test_walk_start_groups(self):

        assert hasattr(self.s.content, 'walk_start_groups')
        groups = dict([(g.name, g) for g in self.s.content.walk_start_groups()])
        assert len(groups) == 1
        assert 'start' in groups

    def test_walk_plugins_groups(self):

        assert hasattr(self.s.content, 'walk_plugins_groups')
        groups = dict([(g.name, g) for g in self.s.content.walk_plugins_groups()])
        assert len(groups) == 1
        assert 'plugins' in groups

    def test_walk_section_resources(self):

        assert hasattr(self.s.content, 'walk_resources_grouped_by_section')

        resources = [resource.name for resource in self.s.content.walk_resources_grouped_by_section()]
        assert len(resources) == 5
        assert 'installation.html' in resources
        assert 'overview.html' in resources
        assert 'templating.html' in resources
        assert 'plugins.html' in resources
        assert 'tags.html' in resources

    def test_walk_start_resources(self):

        assert hasattr(self.s.content, 'walk_resources_grouped_by_start')

        start_resources = [resource.name for resource in self.s.content.walk_resources_grouped_by_start()]
        assert len(start_resources) == 3
        assert 'installation.html' in start_resources
        assert 'overview.html' in start_resources
        assert 'templating.html' in start_resources

    def test_walk_plugins_resources(self):

        assert hasattr(self.s.content, 'walk_resources_grouped_by_plugins')

        plugin_resources = [resource.name for resource in self.s.content.walk_resources_grouped_by_plugins()]
        assert len(plugin_resources) == 2
        assert 'plugins.html' in plugin_resources
        assert 'tags.html' in plugin_resources

