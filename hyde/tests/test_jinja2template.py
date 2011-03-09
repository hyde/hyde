# -*- coding: utf-8 -*-
"""
Use nose
`$ pip install nose`
`$ nosetests`

Code borrowed from rwbench.py from the jinja2 examples
"""
from datetime import datetime
from hyde.ext.templates.jinja import Jinja2Template
from hyde.fs import File, Folder
from hyde.site import Site
from hyde.generator import Generator
from hyde.model import Config

import jinja2
from jinja2.utils import generate_lorem_ipsum
from random import choice, randrange
from util import assert_html_equals
import yaml

from pyquery import PyQuery
from nose.tools import raises, nottest, with_setup

ROOT = File(__file__).parent
JINJA2 = ROOT.child_folder('templates/jinja2')

class Article(object):

    def __init__(self, id):
        self.id = id
        self.href = '/article/%d' % self.id
        self.title = generate_lorem_ipsum(1, False, 5, 10)
        self.user = choice(users)
        self.body = generate_lorem_ipsum()
        self.pub_date = datetime.utcfromtimestamp(randrange(10 ** 9, 2 * 10 ** 9))
        self.published = True

def dateformat(x):
    return x.strftime('%Y-%m-%d')

class User(object):

    def __init__(self, username):
        self.href = '/user/%s' % username
        self.username = username


users = map(User, [u'John Doe', u'Jane Doe', u'Peter Somewhat'])
articles = map(Article, range(20))
navigation = [
    ('index',           'Index'),
    ('about',           'About'),
    ('foo?bar=1',       'Foo with Bar'),
    ('foo?bar=2&s=x',   'Foo with X'),
    ('blah',            'Blub Blah'),
    ('hehe',            'Haha'),
] * 5

context = dict(users=users, articles=articles, page_navigation=navigation)

def test_render():
    """
    Uses pyquery to test the html structure for validity
    """
    t = Jinja2Template(JINJA2.path)
    t.configure(None)
    t.env.filters['dateformat'] = dateformat
    source = File(JINJA2.child('index.html')).read_all()

    html = t.render(source, context)
    actual = PyQuery(html)
    assert actual(".navigation li").length == 30
    assert actual("div.article").length == 20
    assert actual("div.article h2").length == 20
    assert actual("div.article h2 a").length == 20
    assert actual("div.article p.meta").length == 20
    assert actual("div.article div.text").length == 20

def test_typogrify():
    source = """
    {%filter typogrify%}
    One & two
    {%endfilter%}
    """
    t = Jinja2Template(JINJA2.path)
    t.configure(None)
    html = t.render(source, {}).strip()
    assert html == u'One <span class="amp">&amp;</span>&nbsp;two'

def test_spaceless():
    source = """
    {%spaceless%}
    <html>
        <body>
            <ul>
                <li>
                    One
                </li>
                <li>
                    Two
                </li>
                <li>
                    Three
                </li>
            </ul>
        </body>
    </html>
    {%endspaceless%}
    """
    t = Jinja2Template(JINJA2.path)
    t.configure(None)
    html = t.render(source, {}).strip()
    expected = u"""
<html><body><ul><li>
                    One
                </li><li>
                    Two
                </li><li>
                    Three
                </li></ul></body></html>
"""
    assert html.strip() == expected.strip()


def test_markdown():
    source = """
    {%markdown%}
    ### Heading 3
    {%endmarkdown%}
    """
    t = Jinja2Template(JINJA2.path)
    t.configure(None)
    html = t.render(source, {}).strip()
    assert html == u'<h3>Heading 3</h3>'

def test_markdown_with_extensions():
    source = """
    {%markdown%}
    ### Heading 3

    {%endmarkdown%}
    """
    t = Jinja2Template(JINJA2.path)
    s = Site(JINJA2.path)
    c = Config(JINJA2.path, config_dict=dict(markdown=dict(extensions=['headerid'])))
    s.config = c
    t.configure(s)
    html = t.render(source, {}).strip()
    assert html == u'<h3 id="heading_3">Heading 3</h3>'


def test_line_statements():
    source = """
    ---markdown
    ### Heading 3

    --- endmarkdown
    """
    t = Jinja2Template(JINJA2.path)
    s = Site(JINJA2.path)
    c = Config(JINJA2.path, config_dict=dict(markdown=dict(extensions=['headerid'])))
    s.config = c
    t.configure(s)
    html = t.render(source, {}).strip()
    assert html == u'<h3 id="heading_3">Heading 3</h3>'


TEST_SITE = File(__file__).parent.child_folder('_test')

@nottest
def assert_markdown_typogrify_processed_well(include_text, includer_text):
    site = Site(TEST_SITE)
    site.config.plugins = ['hyde.ext.plugins.meta.MetaPlugin']
    inc = File(TEST_SITE.child('content/inc.md'))
    inc.write(include_text)
    site.load()
    gen = Generator(site)
    gen.load_template_if_needed()
    template = gen.template
    html = template.render(includer_text, {}).strip()
    assert html
    q = PyQuery(html)
    assert "is_processable" not in html
    assert "This is a" in q("h1").text()
    assert "heading" in q("h1").text()
    assert q(".amp").length == 1
    return html

class TestJinjaTemplate(object):

    def setUp(self):
        TEST_SITE.make()
        TEST_SITE.parent.child_folder('sites/test_jinja').copy_contents_to(TEST_SITE)

    def tearDown(self):
        TEST_SITE.delete()

    def test_depends(self):
        t = Jinja2Template(JINJA2.path)
        t.configure(None)
        deps = list(t.get_dependencies('index.html'))
        assert len(deps) == 2

        assert 'helpers.html' in deps
        assert 'layout.html' in deps

    def test_depends_multi_level(self):
        site = Site(TEST_SITE)
        JINJA2.copy_contents_to(site.content.source)
        inc = File(TEST_SITE.child('content/inc.md'))
        inc.write("{% extends 'index.html' %}")
        site.load()
        gen = Generator(site)
        gen.load_template_if_needed()
        t = gen.template
        deps = list(t.get_dependencies('inc.md'))

        assert len(deps) == 3

        assert 'helpers.html' in deps
        assert 'layout.html' in deps
        assert 'index.html' in deps

    def test_line_statements_with_blocks(self):
        site = Site(TEST_SITE)
        JINJA2.copy_contents_to(site.content.source)
        inc = File(TEST_SITE.child('content/inc.md'))
        text = """
        {% extends 'index.html' %}
        --- block body
        <div id="article">Heya</div>
        --- endblock
        """
        site.load()
        gen = Generator(site)
        gen.load_template_if_needed()
        template = gen.template
        html = template.render(text, {}).strip()

        assert html
        q = PyQuery(html)
        article = q("#article")
        assert article.length == 1
        assert article.text() == "Heya"


    def test_depends_with_reference_tag(self):
        site = Site(TEST_SITE)
        JINJA2.copy_contents_to(site.content.source)
        inc = File(TEST_SITE.child('content/inc.md'))
        inc.write("{% refer to 'index.html' as index%}")
        site.load()
        gen = Generator(site)
        gen.load_template_if_needed()
        t = gen.template
        deps = list(t.get_dependencies('inc.md'))

        assert len(deps) == 3

        assert 'helpers.html' in deps
        assert 'layout.html' in deps
        assert 'index.html' in deps

    def test_cant_find_depends_with_reference_tag_var(self):
        site = Site(TEST_SITE)
        JINJA2.copy_contents_to(site.content.source)
        inc = File(TEST_SITE.child('content/inc.md'))
        inc.write("{% set ind = 'index.html' %}{% refer to ind as index %}")
        site.load()
        gen = Generator(site)
        gen.load_template_if_needed()
        t = gen.template
        deps = list(t.get_dependencies('inc.md'))

        assert len(deps) == 1

        assert not deps[0]


    def test_can_include_templates_with_processing(self):
        text = """
===
is_processable: False
===

{% filter typogrify %}{% markdown %}
This is a heading
=================

Hyde & Jinja.

{% endmarkdown %}{% endfilter %}
"""


        text2 = """{% include "inc.md"  %}"""
        assert_markdown_typogrify_processed_well(text, text2)


    def test_includetext(self):
        text = """
===
is_processable: False
===

This is a heading
=================

Hyde & Jinja.

"""

        text2 = """{% includetext "inc.md"  %}"""
        assert_markdown_typogrify_processed_well(text, text2)

    def test_reference_is_noop(self):
        text = """
===
is_processable: False
===

{% mark heading %}
This is a heading
=================
{% endmark %}
{% reference content %}
Hyde & Jinja.
{% endreference %}

"""

        text2 = """{% includetext "inc.md"  %}"""
        html = assert_markdown_typogrify_processed_well(text, text2)
        assert "mark" not in html
        assert "reference" not in html

    def test_refer(self):
        text = """
===
is_processable: False
===
{% filter markdown|typogrify %}
{% mark heading %}
This is a heading
=================
{% endmark %}
{% reference content %}
Hyde & Jinja.
{% endreference %}
{% endfilter %}
"""

        text2 = """
{% refer to "inc.md" as inc %}
{% filter markdown|typogrify %}
{{ inc.heading }}
{{ inc.content }}
{% endfilter %}
"""
        html = assert_markdown_typogrify_processed_well(text, text2)
        assert "mark" not in html
        assert "reference" not in html

    def test_refer_with_full_html(self):
        text = """
===
is_processable: False
===
<div class="fulltext">
{% filter markdown|typogrify %}
{% mark heading %}
This is a heading
=================
{% endmark %}
{% reference content %}
Hyde & Jinja.
{% endreference %}
{% endfilter %}
</div>
"""

        text2 = """
{% refer to "inc.md" as inc %}
{{ inc.html('.fulltext') }}
"""
        html = assert_markdown_typogrify_processed_well(text, text2)
        assert "mark" not in html
        assert "reference" not in html

    def test_two_level_refer_with_var(self):
        text = """
===
is_processable: False
===
<div class="fulltext">
{% filter markdown|typogrify %}
{% mark heading %}
This is a heading
=================
{% endmark %}
{% reference content %}
Hyde & Jinja.
{% endreference %}
{% endfilter %}
</div>
"""

        text2 = """
{% set super = 'super.md' %}
{% refer to super as sup %}
<div class="justhead">
{% mark child %}
{{ sup.heading }}
{% endmark %}
{% mark cont %}
{{ sup.content }}
{% endmark %}
</div>
"""
        text3 = """
{% set incu = 'inc.md' %}
{% refer to incu as inc %}
{% filter markdown|typogrify %}
{{ inc.child }}
{{ inc.cont }}
{% endfilter %}
"""

        superinc = File(TEST_SITE.child('content/super.md'))
        superinc.write(text)

        html = assert_markdown_typogrify_processed_well(text2, text3)
        assert "mark" not in html
        assert "reference" not in html


    def test_refer_with_var(self):
        text = """
===
is_processable: False
===
<div class="fulltext">
{% filter markdown|typogrify %}
{% mark heading %}
This is a heading
=================
{% endmark %}
{% reference content %}
Hyde & Jinja.
{% endreference %}
{% endfilter %}
</div>
"""

        text2 = """
{% set incu = 'inc.md' %}
{% refer to incu as inc %}
{{ inc.html('.fulltext') }}
"""
        html = assert_markdown_typogrify_processed_well(text, text2)
        assert "mark" not in html
        assert "reference" not in html


    def test_yaml_tag(salf):

        text = """
{% yaml test %}
one:
    - A
    - B
    - C
two:
    - D
    - E
    - F
{% endyaml %}
{% for section, values in test.items() %}
<ul class="{{ section }}">
    {% for value in values %}
    <li>{{ value }}</li>
    {% endfor %}
</ul>
{% endfor %}
"""
        t = Jinja2Template(JINJA2.path)
        t.configure(None)
        html = t.render(text, {}).strip()
        actual = PyQuery(html)
        assert actual("ul").length == 2
        assert actual("ul.one").length == 1
        assert actual("ul.two").length == 1

        assert actual("li").length == 6

        assert actual("ul.one li").length == 3
        assert actual("ul.two li").length == 3

        ones = [item.text for item in actual("ul.one li")]
        assert ones == ["A", "B", "C"]

        twos = [item.text for item in actual("ul.two li")]
        assert twos == ["D", "E", "F"]