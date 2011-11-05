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

OPTIPNG_SOURCE = File(__file__).parent.child_folder('optipng')
TEST_SITE = File(__file__).parent.parent.child_folder('_test')


class TestOptipng(object):

    def setUp(self):
        TEST_SITE.make()
        TEST_SITE.parent.child_folder(
                    'sites/test_jinja').copy_contents_to(TEST_SITE)
        IMAGES = TEST_SITE.child_folder('content/media/images')
        IMAGES.make()
        OPTIPNG_SOURCE.copy_contents_to(IMAGES)


    def tearDown(self):
        TEST_SITE.delete()

    def test_can_execute_optipng(self):
        s = Site(TEST_SITE)
        s.config.mode = "production"
        s.config.plugins = ['hyde.ext.plugins.optipng.OptiPNGPlugin']
        s.config.optipng = Expando(dict(args=dict(quiet="")))
        source =File(TEST_SITE.child('content/media/images/hyde-lt-b.png'))
        target = File(Folder(s.config.deploy_root_path).child('media/images/hyde-lt-b.png'))
        gen = Generator(s)
        gen.generate_resource_at_path(source)
        assert target.exists
        assert target.size < source.size
