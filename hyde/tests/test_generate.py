 # -*- coding: utf-8 -*-
"""
Use nose
`$ pip install nose`
`$ nosetests`
"""

from hyde.generator import Generator
from hyde.fs import FS, File, Folder
from hyde.model import Config
from hyde.site import Site

from nose.tools import raises, with_setup, nottest
from pyquery import PyQuery

TEST_SITE = File(__file__).parent.child_folder('_test')

class TestGenerator(object):

    def setUp(self):
        TEST_SITE.make()
        TEST_SITE.parent.child_folder('sites/test_jinja').copy_contents_to(TEST_SITE)

    def tearDown(self):
        TEST_SITE.delete()

    def test_generate_resource_from_path(self):
        site = Site(TEST_SITE)
        site.load()
        gen = Generator(site)
        gen.generate_resource_at_path(TEST_SITE.child('content/about.html'))
        about = File(Folder(site.config.deploy_root_path).child('about.html'))
        assert about.exists
        text = about.read_all()
        q = PyQuery(text)
        assert about.name in q("div#main").text()

    def test_generate_resource_from_path_with_is_processable_false(self):
        site = Site(TEST_SITE)
        site.load()
        resource = site.content.resource_from_path(TEST_SITE.child('content/about.html'))
        resource.is_processable = False
        gen = Generator(site)
        gen.generate_resource_at_path(TEST_SITE.child('content/about.html'))
        about = File(Folder(site.config.deploy_root_path).child('about.html'))
        assert not about.exists

    def test_generate_resource_from_path_with_uses_template_false(self):
        site = Site(TEST_SITE)
        site.load()
        resource = site.content.resource_from_path(TEST_SITE.child('content/about.html'))
        resource.uses_template = False
        gen = Generator(site)
        gen.generate_resource_at_path(TEST_SITE.child('content/about.html'))
        about = File(Folder(site.config.deploy_root_path).child('about.html'))
        assert about.exists
        text = about.read_all()
        expected = resource.source_file.read_all()
        assert text == expected

    def test_generate_resource_from_path_with_deploy_override(self):
        site = Site(TEST_SITE)
        site.load()
        resource = site.content.resource_from_path(TEST_SITE.child('content/about.html'))
        resource.relative_deploy_path = 'about/index.html'
        gen = Generator(site)
        gen.generate_resource_at_path(TEST_SITE.child('content/about.html'))
        about = File(Folder(site.config.deploy_root_path).child('about/index.html'))
        assert about.exists
        text = about.read_all()
        q = PyQuery(text)
        assert resource.name in q("div#main").text()

    def test_has_resource_changed(self):
        site = Site(TEST_SITE)
        site.load()
        resource = site.content.resource_from_path(TEST_SITE.child('content/about.html'))
        gen = Generator(site)
        gen.generate_all()
        assert not gen.has_resource_changed(resource)
        import time
        time.sleep(1)
        text = resource.source_file.read_all()
        resource.source_file.write(text)
        assert gen.has_resource_changed(resource)
        gen.generate_all()
        assert not gen.has_resource_changed(resource)
        time.sleep(1)
        l = File(TEST_SITE.child('layout/root.html'))
        l.write(l.read_all())
        assert gen.has_resource_changed(resource)

    def test_context(self):
        site = Site(TEST_SITE, Config(TEST_SITE, config_dict={
            "context": {
                "data": {
                    "abc": "def"
                }
            }
        }))
        text = """
{% extends "base.html" %}

{% block main %}
    abc = {{ abc }}
    Hi!

    I am a test template to make sure jinja2 generation works well with hyde.
    {{resource.name}}
{% endblock %}
"""
        site.load()
        resource = site.content.resource_from_path(TEST_SITE.child('content/about.html'))
        gen = Generator(site)
        resource.source_file.write(text)
        gen.generate_all()
        target = File(site.config.deploy_root_path.child(resource.name))
        assert "abc = def" in target.read_all()

    def test_context_providers(self):
        site = Site(TEST_SITE, Config(TEST_SITE, config_dict={
            "context": {
                "data": {
                    "abc": "def"
                },
                "providers": {
                    "nav": "nav.yaml"
                }
            }
        }))
        nav = """
main:
    - home
    - articles
    - projects
"""
        text = """
{% extends "base.html" %}

{% block main %}
    {{nav}}
    {% for item in nav.main %}
    {{item}}
    {% endfor %}
    abc = {{ abc }}
    Hi!

    I am a test template to make sure jinja2 generation works well with hyde.
    {{resource.name}}
{% endblock %}
"""
        File(TEST_SITE.child('nav.yaml')).write(nav)
        site.load()
        resource = site.content.resource_from_path(TEST_SITE.child('content/about.html'))
        gen = Generator(site)
        resource.source_file.write(text)
        gen.generate_all()
        target = File(site.config.deploy_root_path.child(resource.name))
        out = target.read_all()
        assert "abc = def" in out
        assert "home" in out
        assert "articles" in out
        assert "projects" in out