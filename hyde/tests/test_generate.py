# -*- coding: utf-8 -*-
"""
Use nose
`$ pip install nose`
`$ nosetests`
"""


from hyde.generator import Generator
from hyde.fs import FS, File, Folder
from hyde.site import Site

from nose.tools import raises, with_setup, nottest
from pyquery import PyQuery

TEST_SITE = File(__file__).parent.child_folder('_test')

@nottest
def create_test_site():
    TEST_SITE.make()
    TEST_SITE.parent.child_folder('sites/test_jinja').copy_contents_to(TEST_SITE)

@nottest
def delete_test_site():
    TEST_SITE.delete()

@with_setup(create_test_site, delete_test_site)
def test_generate_resource_from_path():
    site = Site(TEST_SITE)
    site.load()
    gen = Generator(site)
    gen.generate_resource_at_path(TEST_SITE.child('content/about.html'))
    about = File(Folder(site.config.deploy_root_path).child('about.html'))
    assert about.exists
    text = about.read_all()
    q = PyQuery(text)
    assert about.name in q("div#main").text()

@with_setup(create_test_site, delete_test_site)
def test_generate_resource_from_path_with_is_processable_false():
    site = Site(TEST_SITE)
    site.load()
    resource = site.content.resource_from_path(TEST_SITE.child('content/about.html'))
    resource.is_processable = False
    gen = Generator(site)
    gen.generate_resource_at_path(TEST_SITE.child('content/about.html'))
    about = File(Folder(site.config.deploy_root_path).child('about.html'))
    assert not about.exists

@with_setup(create_test_site, delete_test_site)
def test_generate_resource_from_path_with_deploy_override():
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