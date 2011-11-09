# -*- coding: utf-8 -*-
"""
Use nose
`$ pip install nose`
`$ nosetests`
"""
from hyde.fs import File, Folder
from hyde.model import Expando
from hyde.generator import Generator
from hyde.site import Site

UGLIFY_SOURCE = File(__file__).parent.child_folder('uglify')
TEST_SITE = File(__file__).parent.parent.child_folder('_test')


class TestUglify(object):

    def setUp(self):
        TEST_SITE.make()
        TEST_SITE.parent.child_folder(
                    'sites/test_jinja').copy_contents_to(TEST_SITE)
        JS = TEST_SITE.child_folder('content/media/js')
        JS.make()
        UGLIFY_SOURCE.copy_contents_to(JS)


    def tearDown(self):
        TEST_SITE.delete()

    def test_can_uglify(self):
        s = Site(TEST_SITE)
        s.config.plugins = ['hyde.ext.plugins.uglify.UglifyPlugin']
        s.config.mode = "production"
        source = TEST_SITE.child('content/media/js/jquery.js')
        target = File(Folder(s.config.deploy_root_path).child('media/js/jquery.js'))
        gen = Generator(s)
        gen.generate_resource_at_path(source)

        assert target.exists
        expected = File(UGLIFY_SOURCE.child('expected-jquery.js'))
        # TODO: Very fragile. Better comparison needed.
        assert target.read_all() == expected.read_all()

    def test_uglify_with_extra_options(self):
        s = Site(TEST_SITE)
        s.config.plugins = ['hyde.ext.plugins.uglify.UglifyPlugin']
        s.config.mode = "production"
        s.config.uglify = Expando(dict(args={"nc":""}))
        source = TEST_SITE.child('content/media/js/jquery.js')
        target = File(Folder(s.config.deploy_root_path).child('media/js/jquery.js'))
        gen = Generator(s)
        gen.generate_resource_at_path(source)

        assert target.exists
        expected = File(UGLIFY_SOURCE.child('expected-jquery-nc.js'))
        # TODO: Very fragile. Better comparison needed.
        text = target.read_all()
        assert text.startswith("(function(")

    def test_no_uglify_in_dev_mode(self):
        s = Site(TEST_SITE)
        s.config.plugins = ['hyde.ext.plugins.uglify.UglifyPlugin']
        s.config.mode = "dev"
        source = TEST_SITE.child('content/media/js/jquery.js')
        target = File(Folder(s.config.deploy_root_path).child('media/js/jquery.js'))
        gen = Generator(s)
        gen.generate_resource_at_path(source)

        assert target.exists
        expected = File(UGLIFY_SOURCE.child('jquery.js'))
        # TODO: Very fragile. Better comparison needed.
        text = target.read_all()
        expected = expected.read_all()
        assert text == expected


