# -*- coding: utf-8 -*-
"""
Use nose
`$ pip install nose`
`$ nosetests`
"""
from hyde.generator import Generator
from hyde.site import Site

from fswrap import File
from pyquery import PyQuery

TEST_SITE = File(__file__).parent.parent.child_folder('_test')


class TestSyntext(object):

    def setUp(self):
        TEST_SITE.make()
        TEST_SITE.parent.child_folder(
                    'sites/test_jinja').copy_contents_to(TEST_SITE)

    def tearDown(self):
        TEST_SITE.delete()



    def test_syntext(self):
        text = u"""
~~~~~~~~css~~~~~~~
.body{
    background-color: white;
}
~~~~~~~~~~~~~~~~~~
"""
        site = Site(TEST_SITE)
        site.config.plugins = [
            'hyde.ext.plugins.meta.MetaPlugin',
            'hyde.ext.plugins.text.SyntextPlugin']
        syn = File(site.content.source_folder.child('syn.html'))
        syn.write(text)
        gen = Generator(site)
        gen.generate_all()
        f = File(site.config.deploy_root_path.child(syn.name))
        assert f.exists
        html = f.read_all()
        assert html
        q = PyQuery(html)
        assert q('figure.code').length == 1
