# -*- coding: utf-8 -*-
"""
Use nose
`$ pip install nose`
`$ nosetests`
"""
from hyde.generator import Generator
from hyde.site import Site

from fswrap import File, Folder

from util import assert_no_diff

SCSS_SOURCE = File(__file__).parent.child_folder('scss')
TEST_SITE = File(__file__).parent.parent.child_folder('_test')


class TestSass(object):

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
        s.config.mode = 'prod'
        s.config.plugins = ['hyde.ext.plugins.css.SassPlugin']
        s.config.sass = {'files': ['media/css/sass.scss']}
        source = TEST_SITE.child('content/media/css/sass.scss')
        target = File(
            Folder(s.config.deploy_root_path).child('media/css/sass.css'))
        gen = Generator(s)
        gen.generate_resource_at_path(source)

        assert target.exists
        text = target.read_all()
        expected_text = File(SCSS_SOURCE.child('expected-sass.css')).read_all()
        print("TEXT" + "-" * 80)
        print(text)
        print("-" * 80)
        print(expected_text)
        assert_no_diff(expected_text, text)
