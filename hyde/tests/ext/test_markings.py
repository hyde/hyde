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

def assert_valid_conversion(html):
    assert html
    q = PyQuery(html)
    assert "is_processable" not in html
    assert q("h1")
    assert "This is a" in q("h1").text()
    assert "heading" in q("h1").text()
    assert q(".amp").length == 1
    assert "mark" not in html
    assert "reference" not in html
    assert '.' not in q.text()
    assert '/' not in q.text()

class TestMarkings(object):

    def setUp(self):
        TEST_SITE.make()
        TEST_SITE.parent.child_folder(
                    'sites/test_jinja').copy_contents_to(TEST_SITE)

    def tearDown(self):
        TEST_SITE.delete()



    def test_mark(self):
        text = u"""
===
is_processable: False
===
{% filter markdown|typogrify %}
§§ heading
This is a heading
=================
§§ /heading

§§ content
Hyde & Jinja
§§ /

{% endfilter %}
"""

        text2 = """
{% refer to "inc.md" as inc %}
{% filter markdown|typogrify %}
{{ inc.heading }}
{{ inc.content }}
{% endfilter %}
"""
        site = Site(TEST_SITE)
        site.config.plugins = [
            'hyde.ext.plugins.meta.MetaPlugin',
            'hyde.ext.plugins.text.MarkingsPlugin']
        inc = File(TEST_SITE.child('content/inc.md'))
        inc.write(text)
        site.load()
        gen = Generator(site)
        gen.load_template_if_needed()

        template = gen.template
        html = template.render(text2, {}).strip()
        assert_valid_conversion(html)

    def test_reference(self):
        text = u"""
===
is_processable: False
===
{% filter markdown|typogrify %}
§§ heading
This is a heading
=================
§§ /heading

§§ content
Hyde & Jinja
§§ /

{% endfilter %}
"""

        text2 = u"""
※ inc.md as inc
{% filter markdown|typogrify %}
{{ inc.heading }}
{{ inc.content }}
{% endfilter %}
"""
        site = Site(TEST_SITE)
        site.config.plugins = [
            'hyde.ext.plugins.meta.MetaPlugin',
            'hyde.ext.plugins.text.MarkingsPlugin',
            'hyde.ext.plugins.text.ReferencePlugin']
        inc = File(site.content.source_folder.child('inc.md'))
        inc.write(text.strip())
        src = File(site.content.source_folder.child('src.html'))
        src.write(text2.strip())
        gen = Generator(site)
        gen.generate_all()
        f = File(site.config.deploy_root_path.child(src.name))
        assert f.exists
        html = f.read_all()
        assert_valid_conversion(html)
