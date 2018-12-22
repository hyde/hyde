# -*- coding: utf-8 -*-
from hyde.model import Expando
from hyde.generator import Generator
from hyde.site import Site

from fswrap import File, Folder

STYLUS_SOURCE = File(__file__).parent.child_folder('stylus')
TEST_SITE = File(__file__).parent.parent.child_folder('_test')


class TestStylus(object):

    def setUp(self):
        TEST_SITE.make()
        TEST_SITE.parent.child_folder(
            'sites/test_jinja').copy_contents_to(TEST_SITE)
        STYLUS_SOURCE.copy_contents_to(TEST_SITE.child('content/media/css'))
        File(TEST_SITE.child('content/media/css/site.css')).delete()

    def tearDown(self):
        TEST_SITE.delete()

    def test_can_execute_stylus(self):
        s = Site(TEST_SITE)
        s.config.plugins = ['hyde.ext.plugins.css.StylusPlugin']
        source = TEST_SITE.child('content/media/css/site.styl')
        target = File(
            Folder(s.config.deploy_root_path).child('media/css/site.css'))
        gen = Generator(s)
        return
        #gen.generate_resource_at_path(source)

        #assert target.exists
        #text = target.read_all()
        #expected_text = File(
        #    STYLUS_SOURCE.child('expected-site.css')).read_all()
        #assert text.strip() == expected_text.strip()

    def test_can_compress_with_stylus(self):
        s = Site(TEST_SITE)
        s.config.mode = "production"
        s.config.plugins = ['hyde.ext.plugins.css.StylusPlugin']
        source = TEST_SITE.child('content/media/css/site.styl')
        target = File(
            Folder(s.config.deploy_root_path).child('media/css/site.css'))
        gen = Generator(s)
        return
        #gen.generate_resource_at_path(source)

        #assert target.exists
        #text = target.read_all()
        #expected_text = File(
        #    STYLUS_SOURCE.child('expected-site-compressed.css')).read_all()
        #assert text.strip() == expected_text.strip()
