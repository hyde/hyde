# -*- coding: utf-8 -*-
"""
Use nose
`$ pip install nose`
`$ nosetests`
"""
from hyde.generator import Generator
from hyde.site import Site

from fswrap import File, Folder

LESS_SOURCE = File(__file__).parent.child_folder('less')
TEST_SITE = File(__file__).parent.parent.child_folder('_test')


class TestLess(object):

    def setUp(self):
        TEST_SITE.make()
        TEST_SITE.parent.child_folder(
                    'sites/test_jinja').copy_contents_to(TEST_SITE)
        LESS_SOURCE.copy_contents_to(TEST_SITE.child('content/media/css'))
        File(TEST_SITE.child('content/media/css/site.css')).delete()


    def tearDown(self):
        TEST_SITE.delete()

    def test_can_execute_less(self):
        s = Site(TEST_SITE)
        s.config.plugins = ['hyde.ext.plugins.css.LessCSSPlugin']
        source = TEST_SITE.child('content/media/css/site.less')
        target = File(Folder(s.config.deploy_root_path).child('media/css/site.css'))
        gen = Generator(s)
        gen.generate_resource_at_path(source)

        assert target.exists
        text = target.read_all()
        expected_text = File(LESS_SOURCE.child('expected-site.css')).read_all()

        assert text == expected_text
        return
