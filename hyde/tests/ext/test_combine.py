# -*- coding: utf-8 -*-
"""
Use nose
`$ pip install nose`
`$ nosetests`
"""
from hyde.generator import Generator
from hyde.site import Site

from fswrap import File, Folder

COMBINE_SOURCE = File(__file__).parent.child_folder('combine')
TEST_SITE = File(__file__).parent.parent.child_folder('_test')

class CombineTester(object):
    def _test_combine(self, content):
        s = Site(TEST_SITE)
        s.config.plugins = [
            'hyde.ext.plugins.meta.MetaPlugin',
            'hyde.ext.plugins.structure.CombinePlugin']
        source = TEST_SITE.child('content/media/js/script.js')
        target = File(Folder(s.config.deploy_root_path).child('media/js/script.js'))
        File(source).write(content)

        gen = Generator(s)
        gen.generate_resource_at_path(source)

        assert target.exists
        text = target.read_all()
        return text, s

class TestCombine(CombineTester):

    def setUp(self):
        TEST_SITE.make()
        TEST_SITE.parent.child_folder(
                    'sites/test_jinja').copy_contents_to(TEST_SITE)
        TEST_SITE.child_folder('content/media/js').make()
        COMBINE_SOURCE.copy_contents_to(TEST_SITE.child('content/media/js'))

    def tearDown(self):
        TEST_SITE.delete()

    def test_combine_top(self):
        text, _ = self._test_combine("""
---
combine:
   files: script.*.js
   where: top
---

Last line""")
        assert text == """var a = 1 + 2;
var b = a + 3;
var c = a + 5;
Last line"""
        return

    def test_combine_bottom(self):
        text, _ = self._test_combine("""
---
combine:
   files: script.*.js
   where: bottom
---

First line
""")
        expected = """First line
var a = 1 + 2;
var b = a + 3;
var c = a + 5;
"""

        assert text.strip() == expected.strip()
        return

    def test_combine_bottom_unsorted(self):
        text, _ = self._test_combine("""
---
combine:
   sort: false
   files:
        - script.3.js
        - script.1.js
        - script.2.js
   where: bottom
---

First line
""")
        expected = """First line
var c = a + 5;
var a = 1 + 2;
var b = a + 3;
"""

        assert text.strip() == expected.strip()
        return

    def test_combine_remove(self):
        _, s = self._test_combine("""
---
combine:
   files: script.*.js
   remove: yes
---

First line""")
        for i in range(1,4):
            assert not File(Folder(s.config.deploy_root_path).
                            child('media/js/script.%d.js' % i)).exists


class TestCombinePaths(CombineTester):

    def setUp(self):
        TEST_SITE.make()
        TEST_SITE.parent.child_folder(
                    'sites/test_jinja').copy_contents_to(TEST_SITE)
        TEST_SITE.child_folder('content/media/js').make()
        JS = TEST_SITE.child_folder('content/scripts').make()
        S1 = JS.child_folder('s1').make()
        S2 = JS.child_folder('s2').make()
        S3 = JS.child_folder('s3').make()
        File(COMBINE_SOURCE.child('script.1.js')).copy_to(S1)
        File(COMBINE_SOURCE.child('script.2.js')).copy_to(S2)
        File(COMBINE_SOURCE.child('script.3.js')).copy_to(S3)

    def tearDown(self):
        TEST_SITE.delete()

    def test_combine_top(self):
        text, _ = self._test_combine("""
---
combine:
   root: scripts
   recurse: true
   files: script.*.js
   where: top
---

Last line""")
        assert text == """var a = 1 + 2;
var b = a + 3;
var c = a + 5;
Last line"""
        return
