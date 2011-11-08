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

from hyde.tests.util import assert_html_equals
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
          - hyde.ext.plugins.meta.MetaPlugin
          - hyde.ext.plugins.sorter.SorterPlugin
          - hyde.ext.plugins.grouper.GrouperPlugin
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

        self.all = ['installation.html', 'overview.html', 'templating.html', 'plugins.html', 'tags.html']
        self.start = ['installation.html', 'overview.html', 'templating.html']
        self.plugins = ['plugins.html', 'tags.html']
        self.section = self.all

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
        groups = dict([(grouper.group.name, grouper) for grouper in self.s.content.walk_section_groups()])
        assert len(groups) == 3
        assert 'section' in groups
        assert 'start' in groups
        assert 'plugins' in groups
        for name in ['start', 'plugins']:
            res = [resource.name for resource in groups[name].resources]
            assert res == getattr(self, name)

    def test_walk_start_groups(self):

        assert hasattr(self.s.content, 'walk_start_groups')
        groups = dict([(g.name, g) for g, resources in self.s.content.walk_start_groups()])
        assert len(groups) == 1
        assert 'start' in groups


    def test_walk_plugins_groups(self):

        assert hasattr(self.s.content, 'walk_plugins_groups')
        groups = dict([(g.name, g) for g, resources in self.s.content.walk_plugins_groups()])
        assert len(groups) == 1
        assert 'plugins' in groups

    def test_walk_section_resources(self):

        assert hasattr(self.s.content, 'walk_resources_grouped_by_section')

        resources = [resource.name for resource in self.s.content.walk_resources_grouped_by_section()]
        assert resources == self.all


    def test_walk_start_resources(self):

        assert hasattr(self.s.content, 'walk_resources_grouped_by_start')

        start_resources = [resource.name for resource in self.s.content.walk_resources_grouped_by_start()]
        assert start_resources == self.start

    def test_walk_plugins_resources(self):

        assert hasattr(self.s.content, 'walk_resources_grouped_by_plugins')

        plugin_resources = [resource.name for resource in self.s.content.walk_resources_grouped_by_plugins()]
        assert plugin_resources == self.plugins

    def test_resource_group(self):

        groups = dict([(g.name, g) for g in self.s.grouper['section'].groups])

        for name, group in groups.items():
            pages = getattr(self, name)
            for page in pages:
                res = self.s.content.resource_from_relative_path('blog/' + page)
                assert hasattr(res, 'section_group')
                res_group = getattr(res, 'section_group')
                assert res_group == group

    def test_resource_belongs_to(self):

        groups = dict([(g.name, g) for g in self.s.grouper['section'].groups])

        for name, group in groups.items():
            pages = getattr(self, name)
            for page in pages:
                res = self.s.content.resource_from_relative_path('blog/' + page)
                res_groups = getattr(res, 'walk_%s_groups' % name)()
                assert group in res_groups

    def test_prev_next(self):

        resources = []
        for page in self.all:
            resources.append(self.s.content.resource_from_relative_path('blog/' + page))

        index = 0
        for res in resources:
            if index < 4:
                assert res.next_in_section.name == self.all[index + 1]
            else:
                assert not res.next_in_section
            index += 1

        index = 0
        for res in resources:
            if index:
                assert res.prev_in_section.name == self.all[index - 1]
            else:
                assert not res.prev_in_section
            index += 1

    def test_nav_with_grouper(self):

        text ="""
{% for group, resources in site.content.walk_section_groups() %}
<ul>
    <li>
        <h2>{{ group.name|title }}</h2>
        <h3>{{ group.description }}</h3>
        <ul class="links">
            {% for resource in resources %}
            <li>{{resource.name}}</li>
            {% endfor %}
        </ul>
    </li>
</ul>
{% endfor %}

"""
        expected = """
<ul>
    <li>
        <h2>Section</h2>
        <h3>Sections in the site</h3>
        <ul class="links"></ul>
    </li>
</ul>
<ul>
    <li>
        <h2>Start</h2>
        <h3>Getting Started</h3>
        <ul class="links">
            <li>installation.html</li>
            <li>overview.html</li>
            <li>templating.html</li>
        </ul>
    </li>
</ul>
<ul>
    <li>
        <h2>Plugins</h2>
        <h3>Plugins</h3>
        <ul class="links">
            <li>plugins.html</li>
            <li>tags.html</li>
        </ul>
    </li>
</ul>

"""

        gen = Generator(self.s)
        gen.load_site_if_needed()
        gen.load_template_if_needed()
        out = gen.template.render(text, {'site':self.s})
        assert_html_equals(out, expected)

    def test_nav_with_grouper_sorted(self):

        cfg = """
        nodemeta: meta.yaml
        plugins:
          - hyde.ext.plugins.meta.MetaPlugin
          - hyde.ext.plugins.sorter.SorterPlugin
          - hyde.ext.plugins.grouper.GrouperPlugin
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
                      name: awesome
                      description: Awesome
                  -
                      name: plugins
                      description: Plugins

        """
        self.s.config = Config(TEST_SITE, config_dict=yaml.load(cfg))
        self.s.load()
        MetaPlugin(self.s).begin_site()
        SorterPlugin(self.s).begin_site()
        GrouperPlugin(self.s).begin_site()

        text ="""
{% set sorted = site.grouper['section'].groups|sort(attribute='name') %}
{% for group in sorted %}
<ul>
    <li>
        <h2>{{ group.name|title }}</h2>
        <h3>{{ group.description }}</h3>
        <ul class="links">
            {% for resource in group.walk_resources_in_node(site.content) %}
            <li>{{resource.name}}</li>
            {% endfor %}
        </ul>
    </li>
</ul>
{% endfor %}

"""
        expected = """
<ul>
    <li>
        <h2>Awesome</h2>
        <h3>Awesome</h3>
        <ul class="links">
        </ul>
    </li>
</ul>
<ul>
    <li>
        <h2>Plugins</h2>
        <h3>Plugins</h3>
        <ul class="links">
            <li>plugins.html</li>
            <li>tags.html</li>
        </ul>
    </li>
</ul>
<ul>
    <li>
        <h2>Start</h2>
        <h3>Getting Started</h3>
        <ul class="links">
            <li>installation.html</li>
            <li>overview.html</li>
            <li>templating.html</li>
        </ul>
    </li>
</ul>


"""
        self.s.config.grouper.section.groups.append(Expando({"name": "awesome", "description": "Aweesoome"}));
        gen = Generator(self.s)
        gen.load_site_if_needed()
        gen.load_template_if_needed()
        out = gen.template.render(text, {'site':self.s})
        assert_html_equals(out, expected)