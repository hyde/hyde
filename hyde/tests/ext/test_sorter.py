# -*- coding: utf-8 -*-
"""
Use nose
`$ pip install nose`
`$ nosetests`
"""
from hyde.ext.plugins.meta import MetaPlugin
from hyde.ext.plugins.sorter import SorterPlugin
from hyde.fs import File, Folder
from hyde.generator import Generator
from hyde.site import Site
from hyde.model import Config, Expando
import yaml

from operator import attrgetter

TEST_SITE = File(__file__).parent.parent.child_folder('_test')


class TestSorter(object):

    def setUp(self):
        TEST_SITE.make()
        TEST_SITE.parent.child_folder(
                    'sites/test_jinja').copy_contents_to(TEST_SITE)

    def tearDown(self):
        TEST_SITE.delete()

    def test_walk_resources_sorted(self):
        s = Site(TEST_SITE)
        s.load()
        s.config.plugins = ['hyde.ext.sorter.SorterPlugin']
        s.config.sorter = Expando(dict(kind=dict(attr=['source_file.kind', 'name'])))

        SorterPlugin(s).begin_site()

        assert hasattr(s.content, 'walk_resources_sorted_by_kind')
        expected = ["404.html",
                    "about.html",
                    "apple-touch-icon.png",
                    "merry-christmas.html",
                    "crossdomain.xml",
                    "favicon.ico",
                    "robots.txt",
                    "site.css"
                    ]

        pages = [page.name for page in
                s.content.walk_resources_sorted_by_kind()]

        assert pages == sorted(expected, key=lambda f: (File(f).kind, f))

    def test_walk_resources_sorted_reverse(self):
        s = Site(TEST_SITE)
        s.load()
        s.config.plugins = ['hyde.ext.sorter.SorterPlugin']
        s.config.sorter = Expando(dict(kind=dict(attr=['source_file.kind', 'name'], reverse=True)))

        SorterPlugin(s).begin_site()

        assert hasattr(s.content, 'walk_resources_sorted_by_kind')
        expected = ["404.html",
                    "about.html",
                    "apple-touch-icon.png",
                    "merry-christmas.html",
                    "crossdomain.xml",
                    "favicon.ico",
                    "robots.txt",
                    "site.css"
                    ]

        pages = [page.name for page in
                s.content.walk_resources_sorted_by_kind()]


        assert pages == sorted(expected, key=lambda f: (File(f).kind, f), reverse=True)

    def test_walk_resources_sorted_with_filters(self):
        s = Site(TEST_SITE)
        cfg = """
        plugins:
            - hyde.ext.sorter.SorterPlugin
        sorter:
            kind2:
                filters:
                    source_file.kind: html
        """
        s.config = Config(TEST_SITE, config_dict=yaml.load(cfg))
        s.load()
        SorterPlugin(s).begin_site()

        assert hasattr(s.content, 'walk_resources_sorted_by_kind2')
        expected = ["404.html",
                    "about.html",
                    "merry-christmas.html"
                    ]

        pages = [page.name for page in s.content.walk_resources_sorted_by_kind2()]

        assert pages == sorted(expected)

    def test_walk_resources_sorted_with_multiple_attributes(self):
        s = Site(TEST_SITE)
        cfg = """
        plugins:
            - hyde.ext.sorter.SorterPlugin
        sorter:
            multi:
                attr:
                    - source_file.kind
                    - node.name
                    - name

        """
        s.config = Config(TEST_SITE, config_dict=yaml.load(cfg))
        s.load()
        SorterPlugin(s).begin_site()

        assert hasattr(s.content, 'walk_resources_sorted_by_multi')
        expected = ["content/404.html",
                    "content/about.html",
                    "content/apple-touch-icon.png",
                    "content/blog/2010/december/merry-christmas.html",
                    "content/crossdomain.xml",
                    "content/favicon.ico",
                    "content/robots.txt",
                    "content/site.css"
                    ]

        pages = [page.name for page in s.content.walk_resources_sorted_by_multi()]

        expected_sorted = [File(page).name
                                for page in
                                    sorted(expected,
                                        key=lambda p: tuple(
                                            [File(p).kind,
                                            File(p).parent.name, p]))]
        assert pages == expected_sorted

    def test_walk_resources_sorted_no_default_is_processable(self):
        s = Site(TEST_SITE)
        cfg = """
        plugins:
            - hyde.ext.sorter.SorterPlugin
        sorter:
            kind2:
                filters:
                    source_file.kind: html
                attr:
                    - name
        """
        s.config = Config(TEST_SITE, config_dict=yaml.load(cfg))
        s.load()
        p_404 = s.content.resource_from_relative_path('404.html')
        p_404.is_processable = False
        SorterPlugin(s).begin_site()

        assert hasattr(s.content, 'walk_resources_sorted_by_kind2')
        expected = ["404.html", "about.html", "merry-christmas.html"]

        pages = [page.name for page in s.content.walk_resources_sorted_by_kind2()]

        assert pages == sorted(expected)

    def test_prev_next(self):
        s = Site(TEST_SITE)
        cfg = """
        plugins:
            - hyde.ext.sorter.SorterPlugin
        sorter:
            kind2:
                filters:
                    source_file.kind: html
                attr:
                    - name
        """
        s.config = Config(TEST_SITE, config_dict=yaml.load(cfg))
        s.load()
        SorterPlugin(s).begin_site()

        p_404 = s.content.resource_from_relative_path('404.html')
        p_about = s.content.resource_from_relative_path('about.html')
        p_mc = s.content.resource_from_relative_path(
                            'blog/2010/december/merry-christmas.html')

        assert hasattr(p_404, 'prev_by_kind2')
        assert not p_404.prev_by_kind2
        assert hasattr(p_404, 'next_by_kind2')
        assert p_404.next_by_kind2 == p_about

        assert hasattr(p_about, 'prev_by_kind2')
        assert p_about.prev_by_kind2 == p_404
        assert hasattr(p_about, 'next_by_kind2')
        assert p_about.next_by_kind2 == p_mc

        assert hasattr(p_mc, 'prev_by_kind2')
        assert p_mc.prev_by_kind2 == p_about
        assert hasattr(p_mc, 'next_by_kind2')
        assert not p_mc.next_by_kind2

    def test_prev_next_reversed(self):
          s = Site(TEST_SITE)
          cfg = """
          plugins:
              - hyde.ext.sorter.SorterPlugin
          sorter:
              folder_name:
                  attr:
                    - node.name
                  reverse: True
                  filters:
                      source_file.kind: html
          """
          s.config = Config(TEST_SITE, config_dict=yaml.load(cfg))
          s.load()
          SorterPlugin(s).begin_site()

          p_404 = s.content.resource_from_relative_path('404.html')
          p_about = s.content.resource_from_relative_path('about.html')
          p_mc = s.content.resource_from_relative_path(
                              'blog/2010/december/merry-christmas.html')

          assert hasattr(p_mc, 'prev_by_folder_name')
          assert not p_mc.prev_by_folder_name
          assert hasattr(p_mc, 'next_by_folder_name')
          assert p_mc.next_by_folder_name == p_404

          assert hasattr(p_404, 'prev_by_folder_name')
          assert p_404.prev_by_folder_name == p_mc
          assert hasattr(p_404, 'next_by_folder_name')
          assert p_404.next_by_folder_name == p_about

          assert hasattr(p_about, 'prev_by_folder_name')
          assert p_about.prev_by_folder_name == p_404
          assert hasattr(p_about, 'next_by_folder_name')
          assert not p_about.next_by_folder_name

    def test_walk_resources_sorted_using_generator(self):
           s = Site(TEST_SITE)
           cfg = """
           meta:
               time: !!timestamp 2010-10-23
               title: NahNahNah
           plugins:
               - hyde.ext.plugins.meta.MetaPlugin
               - hyde.ext.plugins.sorter.SorterPlugin
           sorter:
               time:
                   attr: meta.time
                   filters:
                       source_file.kind: html
           """
           s.config = Config(TEST_SITE, config_dict=yaml.load(cfg))
           text = """
   ---
    time: !!timestamp 2010-12-31
    title: YayYayYay
   ---
   {% extends "base.html" %}

   {% block main %}
       {% set latest = site.content.walk_resources_sorted_by_time()|reverse|first %}
       <span class="latest">{{ latest.meta.title }}</span>
   {% endblock %}
   """

           about2 = File(TEST_SITE.child('content/about2.html'))
           about2.write(text)
           gen = Generator(s)
           gen.generate_all()

           from pyquery import PyQuery
           target = File(Folder(s.config.deploy_root_path).child('about2.html'))
           text = target.read_all()
           q = PyQuery(text)

           assert q('span.latest').text() == 'YayYayYay'

class TestSorterMeta(object):

   def setUp(self):
       TEST_SITE.make()
       TEST_SITE.parent.child_folder(
                   'sites/test_sorter').copy_contents_to(TEST_SITE)

   def tearDown(self):
       TEST_SITE.delete()

   def test_attribute_checker_no_meta(self):
       s = Site(TEST_SITE)
       s.load()
       from hyde.ext.plugins.sorter import attributes_checker
       for r in s.content.walk_resources():
           assert not attributes_checker(r, ['meta.index'])

   def test_attribute_checker_with_meta(self):
       s = Site(TEST_SITE)
       s.load()
       MetaPlugin(s).begin_site()
       from hyde.ext.plugins.sorter import attributes_checker
       have_index = ["angry-post.html",
                   "another-sad-post.html",
                   "happy-post.html"]
       for r in s.content.walk_resources():
           expected = r.name in have_index
           assert attributes_checker(r, ['meta.index']) == expected


   def test_walk_resources_sorted_by_index(self):
       s = Site(TEST_SITE)
       s.load()
       config = {
        "index": {
            "attr": ['meta.index', 'name']
        }
       }
       s.config.sorter = Expando(config)
       MetaPlugin(s).begin_site()
       SorterPlugin(s).begin_site()

       assert hasattr(s.content, 'walk_resources_sorted_by_index')
       expected = ["angry-post.html",
                   "another-sad-post.html",
                   "happy-post.html"]

       pages = [page.name for page in
               s.content.walk_resources_sorted_by_index()]

       assert pages == sorted(expected, key=lambda f: (File(f).kind, f))
