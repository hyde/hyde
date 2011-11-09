# -*- coding: utf-8 -*-
"""
Use nose
`$ pip install nose`
`$ nosetests`
"""
from hyde.fs import File, Folder
from hyde.generator import Generator
from hyde.site import Site
from urllib import quote

from pyquery import PyQuery

TEST_SITE = File(__file__).parent.parent.child_folder('_test')


class TestTextlinks(object):

    def setUp(self):
        TEST_SITE.make()
        TEST_SITE.parent.child_folder(
                    'sites/test_jinja').copy_contents_to(TEST_SITE)

    def tearDown(self):
        TEST_SITE.delete()



    def test_textlinks(self):
        d = {
            'objects': 'template/variables',
            'plugins': 'plugins/metadata',
            'sorter': 'plugins/sorter'
        }
        text = u"""
{%% markdown %%}
[[!!img/hyde-logo.png]]
*   [Rich object model][hyde objects] and
    [overridable hierarchical metadata]([[ %(plugins)s ]]) thats available for use in
    templates.
*   Configurable [sorting][], filtering and grouping support.

[hyde objects]: [[ %(objects)s ]]
[sorting]: [[%(sorter)s]]
{%% endmarkdown %%}
"""
        site = Site(TEST_SITE)
        site.config.plugins = ['hyde.ext.plugins.textlinks.TextlinksPlugin']
        site.config.base_url = 'http://example.com/'
        site.config.media_url = '/media'
        tlink = File(site.content.source_folder.child('tlink.html'))
        tlink.write(text % d)
        gen = Generator(site)
        gen.generate_all()
        f = File(site.config.deploy_root_path.child(tlink.name))
        assert f.exists
        html = f.read_all()
        assert html
        for name, path in d.items():
            assert quote(site.config.base_url + path) in html
        assert '/media/img/hyde-logo.png' in html