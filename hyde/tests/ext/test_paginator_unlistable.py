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

class TestPaginatorUnlistable(object):

    def setUp(self):
        TEST_SITE.make()
        TEST_SITE.parent.child_folder(
                  'sites/test_paginator_unlistable').copy_contents_to(TEST_SITE)
        self.s = Site(TEST_SITE)
        self.deploy = TEST_SITE.child_folder('deploy')

    def tearDown(self):
        TEST_SITE.delete()

    def test_build(self):
        self.gen = Generator(self.s)
        self.gen.load_site_if_needed()
        self.gen.load_template_if_needed()
        self.gen.generate_all()

