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
        s.config.plugins = ['hyde.ext.plugins.less.LessCSSPlugin']
        paths = ['/usr/local/share/npm/bin/lessc', '~/local/bin/lessc',
                 '/usr/bin/lessc', '~/bin/lessc']
        less = [path for path in paths if File(path).exists]
        if not less:
            assert False, "Cannot find the lessc executable"
        less = less[0]
        s.config.less = Expando(dict(app=less))
        source = TEST_SITE.child('content/media/css/site.less')
        target = File(Folder(s.config.deploy_root_path).child('media/css/site.css'))
        gen = Generator(s)
        gen.generate_resource_at_path(source)

        assert target.exists
        text = target.read_all()
        expected_text = File(LESS_SOURCE.child('expected-site.css')).read_all()

        assert text == expected_text
        return
