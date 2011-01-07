# -*- coding: utf-8 -*-
"""
Use nose
`$ pip install nose`
`$ nosetests`
"""
from hyde.ext.plugins.sorter import SorterPlugin
from hyde.fs import File, Folder
from hyde.generator import Generator
from hyde.site import Site
from hyde.model import Config, Expando
import yaml

TEST_SITE = File(__file__).parent.parent.child_folder('_test')


class TestMeta(object):

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
        s.config.sorter = Expando(dict(kind=dict(attr='source_file.kind')))

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


        assert pages == sorted(expected, key=lambda f: File(f).kind)

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

    def test_prev_next(self):
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

