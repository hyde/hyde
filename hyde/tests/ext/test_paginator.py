# -*- coding: utf-8 -*-
"""
Use nose
`$ pip install nose`
`$ nosetests`
"""
from textwrap import dedent

from hyde.fs import File, Folder
from hyde.generator import Generator
from hyde.model import Expando
from hyde.site import Site

TEST_SITE = File(__file__).parent.parent.child_folder('_test')

class TestTagger(object):

    def setUp(self):
        TEST_SITE.make()
        TEST_SITE.parent.child_folder(
                  'sites/test_paginator').copy_contents_to(TEST_SITE)
        self.s = Site(TEST_SITE)
        self.deploy = TEST_SITE.child_folder('deploy')

        gen = Generator(self.s)
        gen.load_site_if_needed()
        gen.load_template_if_needed()
        gen.generate_all()


    def tearDown(self):
        TEST_SITE.delete()


    def test_pages_of_one(self):
        pages = ['pages_of_one.txt', 'page2/pages_of_one.txt',
                    'page3/pages_of_one.txt', 'page4/pages_of_one.txt']
        files = [File(self.deploy.child(p)) for p in pages]
        for f in files:
            assert f.exists

        page5 = File(self.deploy.child('page5/pages_of_one.txt'))
        assert not page5.exists

    def test_pages_of_one_content(self):
        expected_page1_content = dedent('''\
            Another Sad Post
            page2/pages_of_one.txt
            ''')
        expected_page2_content = dedent('''\
            A Happy Post
            page2/pages_of_one.txt
            page3/pages_of_one.txt
            ''')
        expected_page3_content = dedent('''\
            An Angry Post
            page3/pages_of_one.txt
            page4/pages_of_one.txt
            ''')
        expected_page4_content = dedent('''\
            A Sad Post
            page4/pages_of_one.txt
            ''')

        page1 = self.deploy.child('pages_of_one.txt')
        content = File(page1).read_all()
        assert expected_page1_content == content


    def test_pages_of_ten(self):
        page1 = self.deploy.child('pages_of_ten.txt')
        page2 = self.deploy.child('page2/pages_of_ten.txt')

        assert File(page1).exists
        assert not File(page2).exists


    def test_pages_of_one_content(self):
        expected_content = dedent('''\
            Another Sad Post
            A Happy Post
            An Angry Post
            A Sad Post
            ''')

        page = self.deploy.child('pages_of_ten.txt')
        content = File(page).read_all()
        assert expected_content == content


    def text_custom_file_pattern(self):
        page1 = 'custom_file_pattern.txt'
        page2 = 'custom_file_pattern-2.txt'

        assert File(page1).exists
        assert File(page2).exists
