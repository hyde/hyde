# -*- coding: utf-8 -*-
"""
Use nose
`$ pip install nose`
`$ nosetests`
"""
from hyde.generator import Generator
from hyde.site import Site

from fswrap import File, Folder

RJS_SOURCE = File(__file__).parent.child_folder('requirejs')
TEST_SITE = File(__file__).parent.parent.child_folder('_test')

class TestRequireJS(object):
    def setUp(self):
        TEST_SITE.make()
        TEST_SITE.parent.child_folder('sites/test_jinja').copy_contents_to(TEST_SITE)
        RJS_SOURCE.copy_contents_to(TEST_SITE.child('content/media/js'))
        File(TEST_SITE.child('content/media/js/app.js')).delete()

    def tearDown(self):
        TEST_SITE.delete()

    def test_can_execute_rjs(self):
        s = Site(TEST_SITE)
        s.config.plugins = ['hyde.ext.plugins.js.RequireJSPlugin']
        source = TEST_SITE.child('content/media/js/rjs.conf')
        target = File(Folder(s.config.deploy_root_path).child('media/js/app.js'))
        gen = Generator(s)
        gen.generate_resource_at_path(source)

        assert target.exists
        text = target.read_all()
        expected_text = File(RJS_SOURCE.child('app.js')).read_all()

        assert text == expected_text
        return
