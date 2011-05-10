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

STYLUS_SOURCE = File(__file__).parent.child_folder('stylus')
TEST_SITE = File(__file__).parent.parent.child_folder('_test')


class TestLess(object):

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
        s.config.plugins = ['hyde.ext.plugins.stylus.StylusPlugin']
        paths = ['/usr/local/share/npm/bin/stylus', '~/local/bin/stylus',
                 '~/bin/stylus']
        stylus = [path for path in paths if File(path).exists]
        if not stylus:
            assert False, "Cannot find the stylus executable"

        stylus = stylus[0]
        s.config.stylus = Expando(dict(app=stylus))
        source = TEST_SITE.child('content/media/css/site.styl')
        target = File(Folder(s.config.deploy_root_path).child('media/css/site.css'))
        gen = Generator(s)
        gen.generate_resource_at_path(source)

        assert target.exists
        text = target.read_all()
        expected_text = File(STYLUS_SOURCE.child('expected-site.css')).read_all()
        print text.strip()
        print "=" * 80
        print expected_text.strip()
        assert text.strip() == expected_text.strip()

    def test_can_compress_with_stylus(self):
        s = Site(TEST_SITE)
        s.config.mode = "production"
        s.config.plugins = ['hyde.ext.plugins.stylus.StylusPlugin']
        paths = ['/usr/local/share/npm/bin/stylus', '~/local/bin/stylus',
                 '~/bin/stylus']
        stylus = [path for path in paths if File(path).exists]
        if not stylus:
            assert False, "Cannot find the stylus executable"

        stylus = stylus[0]
        s.config.stylus = Expando(dict(app=stylus))
        source = TEST_SITE.child('content/media/css/site.styl')
        target = File(Folder(s.config.deploy_root_path).child('media/css/site.css'))
        gen = Generator(s)
        gen.generate_resource_at_path(source)

        assert target.exists
        text = target.read_all()
        expected_text = File(STYLUS_SOURCE.child('expected-site-compressed.css')).read_all()
        assert text.strip() == expected_text.strip()
