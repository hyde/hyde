# -*- coding: utf-8 -*-
"""
Use nose
`$ pip install nose`
`$ nosetests`
"""
from hyde.generator import Generator
from hyde.model import Config
from hyde.site import Site

from fswrap import File, Folder
import yaml

TEST_SITE = File(__file__).parent.parent.child_folder('_test')


class TestUrlCleaner(object):

    def setUp(self):
        TEST_SITE.make()
        TEST_SITE.parent.child_folder(
                    'sites/test_jinja').copy_contents_to(TEST_SITE)

    def tearDown(self):
        TEST_SITE.delete()

    def test_url_cleaner(self):
           s = Site(TEST_SITE)
           cfg = """
           plugins:
                - hyde.ext.plugins.urls.UrlCleanerPlugin
           urlcleaner:
                index_file_names:
                    - about.html
                strip_extensions:
                    - html
                append_slash: true
           """
           s.config = Config(TEST_SITE, config_dict=yaml.load(cfg))
           text = """
   {% extends "base.html" %}

   {% block main %}
   <a id="index" href="{{ content_url('about.html') }}"></a>
   <a id="blog" href="{{ content_url('blog/2010/december/merry-christmas.html') }}"></a>
   {% endblock %}
   """

           about2 = File(TEST_SITE.child('content/test.html'))
           about2.write(text)
           gen = Generator(s)
           gen.generate_all()

           from pyquery import PyQuery
           target = File(Folder(s.config.deploy_root_path).child('test.html'))
           text = target.read_all()
           q = PyQuery(text)
           assert q('a#index').attr("href") == '/'
           assert q('a#blog').attr("href") == '/blog/2010/december/merry-christmas'