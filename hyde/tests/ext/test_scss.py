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

SCSS_SOURCE = File(__file__).parent.child_folder('scss')
TEST_SITE = File(__file__).parent.parent.child_folder('_test')


class TestSassyCSS(object):

    def setUp(self):
        TEST_SITE.make()
        TEST_SITE.parent.child_folder(
                    'sites/test_jinja').copy_contents_to(TEST_SITE)
        SCSS_SOURCE.copy_contents_to(TEST_SITE.child('content/media/css'))
        File(TEST_SITE.child('content/media/css/site.css')).delete()


    def tearDown(self):
        TEST_SITE.delete()

    def test_scss(self):
        s = Site(TEST_SITE)
        s.config.plugins = ['hyde.ext.plugins.css.SassyCSSPlugin']
        source = TEST_SITE.child('content/media/css/site.scss')
        target = File(Folder(s.config.deploy_root_path).child('media/css/site.css'))
        gen = Generator(s)
        gen.generate_resource_at_path(source)

        assert target.exists
        text = target.read_all()
        expected_text = File(SCSS_SOURCE.child('expected-site.css')).read_all()

        assert text == expected_text
        return

