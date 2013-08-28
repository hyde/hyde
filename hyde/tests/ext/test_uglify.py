# -*- coding: utf-8 -*-
"""
Use nose
`$ pip install nose`
`$ nosetests`
"""
from hyde.model import Expando
from hyde.generator import Generator
from hyde.site import Site

from fswrap import File, Folder
from hyde.tests.util import assert_no_diff

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
        s.config.plugins = ['hyde.ext.plugins.js.UglifyPlugin']
        s.config.mode = "production"
        source = TEST_SITE.child('content/media/js/jquery.js')
        target = File(Folder(s.config.deploy_root_path).child('media/js/jquery.js'))
        gen = Generator(s)
        gen.generate_resource_at_path(source)

        assert target.exists
        expected = UGLIFY_SOURCE.child_file('expected-jquery.js').read_all()
        # TODO: Very fragile. Better comparison needed.
        text = target.read_all()
        assert_no_diff(expected, text)

    def test_uglify_with_extra_options(self):
        s = Site(TEST_SITE)
        s.config.plugins = ['hyde.ext.plugins.js.UglifyPlugin']
        s.config.mode = "production"
        s.config.uglify = Expando(dict(args={"comments":"/http\:\/\/jquery.org\/license/"}))
        source = TEST_SITE.child('content/media/js/jquery.js')
        target = File(Folder(s.config.deploy_root_path).child('media/js/jquery.js'))
        gen = Generator(s)
        gen.generate_resource_at_path(source)

        assert target.exists
        expected = UGLIFY_SOURCE.child_file('expected-jquery-nc.js').read_all()
        # TODO: Very fragile. Better comparison needed.
        text = target.read_all()
        assert_no_diff(expected, text)

    def test_no_uglify_in_dev_mode(self):
        s = Site(TEST_SITE)
        s.config.plugins = ['hyde.ext.plugins.js.UglifyPlugin']
        s.config.mode = "dev"
        source = TEST_SITE.child('content/media/js/jquery.js')
        target = File(Folder(s.config.deploy_root_path).child('media/js/jquery.js'))
        gen = Generator(s)
        gen.generate_resource_at_path(source)

        assert target.exists
        expected = UGLIFY_SOURCE.child_file('jquery.js').read_all()
        # TODO: Very fragile. Better comparison needed.
        text = target.read_all()
        assert_no_diff(expected, text)


