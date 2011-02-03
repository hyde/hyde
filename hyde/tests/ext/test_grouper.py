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


class TestGrouper(object):

    def setUp(self):
        TEST_SITE.make()
        TEST_SITE.parent.child_folder(
                  'sites/test_grouper').copy_contents_to(TEST_SITE)

    def tearDown(self):
        TEST_SITE.delete()

    def test_walk_resources_sorted_with_grouping_one_level(self):
        s = Site(TEST_SITE)
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
        s.config = Config(TEST_SITE, config_dict=yaml.load(cfg))
        s.load()
        MetaPlugin(s).begin_site()
        SorterPlugin(s).begin_site()
        GrouperPlugin(s).begin_site()

        print [resource.name for resource in s.content.walk_resources_sorted_by_kind()]
        groups = dict([(g.name, g) for g in s.grouper['section'].groups])
        assert len(groups) == 2
        assert 'start' in groups
        assert 'plugins' in groups
        
        groups = dict([(g.name, g) for g in s.grouper['section'].walk_groups()])
        assert len(groups) == 3
        assert 'section' in groups
        assert 'start' in groups
        assert 'plugins' in groups
        
        assert hasattr(s.content, 'walk_section_groups')
        groups = dict([(g.name, g) for g in s.content.walk_section_groups()])
        assert len(groups) == 2
        assert 'start' in groups
        assert 'plugins' in groups

        assert hasattr(s.content, 'walk_resources_grouped_by_section')
        
        resources = [resource.name for resource in s.content.walk_resources_grouped_by_section()]
        
        assert len(resources) == 5

        # assert hasattr(s, 'sectional')
        #        assert hasattr(s.sectional, 'groups')
        #        assert len(s.sectional.groups) == 2
        #
        #        groups = dict([(g.name, g) for g in s.sectional.groups])
        #
        #        assert 'start' in groups
        #        assert 'plugins' in groups
        #
        #        start = groups['start']
        #        assert hasattr(start, 'resources')
        #        start_resources = [resource.name for resource in
        #                                start.resources if resource.is_processable]
        #        assert len(start_resources) == 3
        #        assert 'installation.html' in start_resources
        #        assert 'overview.html' in start_resources
        #        assert 'templating.html' in start_resources
        #
        #        plugin = groups['plugins']
        #        assert hasattr(plugin, 'resources')
        #        plugin_resources = [resource.name for resource in
        #                                plugin.resources if resource.is_processable]
        #        assert len(plugin_resources) == 2
        #        assert 'plugins.html' in plugin_resources
        #        assert 'tags.html' in plugin_resources
        #
        #