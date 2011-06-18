# -*- coding: utf-8 -*-
"""
Use nose
`$ pip install nose`
`$ nosetests`

Requires PIL
"""
from hyde.fs import File, Folder
from hyde.generator import Generator
from hyde.site import Site

from pyquery import PyQuery

TEST_SITE = File(__file__).parent.parent.child_folder('_test')
IMAGE_SOURCE = File(__file__).parent.child_folder('optipng')
IMAGE_NAME = "hyde-lt-b.png"
IMAGE_SIZE = (538, 132)

# PIL requirement
import Image

class TestImageSizer(object):

    def setUp(self):
        TEST_SITE.make()
        TEST_SITE.parent.child_folder(
                    'sites/test_jinja').copy_contents_to(TEST_SITE)
        IMAGES = TEST_SITE.child_folder('content/media/img')
        IMAGES.make()
        IMAGE_SOURCE.copy_contents_to(IMAGES)
        self.site = Site(TEST_SITE)

    def tearDown(self):
        TEST_SITE.delete()

    def _generic_test_image(self, text):
        self.site.config.mode = "production"
        self.site.config.plugins = ['hyde.ext.plugins.images.ImageSizerPlugin']
        tlink = File(self.site.content.source_folder.child('timg.html'))
        tlink.write(text)
        gen = Generator(self.site)
        gen.generate_all()
        f = File(self.site.config.deploy_root_path.child(tlink.name))
        assert f.exists
        html = f.read_all()
        assert html
        return html

    def test_size_image(self):
        text = u"""
<img src="/media/img/%s">
""" % IMAGE_NAME
        html = self._generic_test_image(text)
        assert ' width="%d"' % IMAGE_SIZE[0] in html
        assert ' height="%d"' % IMAGE_SIZE[1] in html

    def test_size_image_relative(self):
        text = u"""
<img src="media/img/%s">
""" % IMAGE_NAME
        html = self._generic_test_image(text)
        assert ' width="%d"' % IMAGE_SIZE[0] in html
        assert ' height="%d"' % IMAGE_SIZE[1] in html

    def test_size_image_no_resize(self):
        text = u"""
<img src="/media/img/%s" width="2000" height="150">
""" % IMAGE_NAME
        html = self._generic_test_image(text)
        assert ' width="%d"' % IMAGE_SIZE[0] not in html
        assert ' height="%d"' % IMAGE_SIZE[1] not in html

    def test_size_image_size_proportional(self):
        text = u"""
<img src="/media/img/%s" width="%d">
""" % (IMAGE_NAME,  IMAGE_SIZE[0]*2)
        html = self._generic_test_image(text)
        assert ' width="%d"' % (IMAGE_SIZE[0]*2) in html
        assert ' height="%d"' % (IMAGE_SIZE[1]*2) in html

    def test_size_image_not_exists(self):
        text = u"""
<img src="/media/img/hyde-logo-no.png">
"""
        html = self._generic_test_image(text)

    def test_size_image_multiline(self):
        text = u"""
     <img 
src="/media/img/%s">
""" % IMAGE_NAME
        html = self._generic_test_image(text)
        assert ' width="%d"' % IMAGE_SIZE[0] in html
        assert ' height="%d"' % IMAGE_SIZE[1] in html

    def test_size_multiple_images(self):
        text = u"""
<img src="/media/img/%s">
<img src="/media/img/%s">Hello <img src="/media/img/%s">
<img src="/media/img/%s">Bye
""" % ((IMAGE_NAME,)*4)
        html = self._generic_test_image(text)
        assert ' width="%d"' % IMAGE_SIZE[0] in html
        assert ' height="%d"' % IMAGE_SIZE[1] in html
        assert 'Hello ' in html
        assert 'Bye' in html
        assert len([f for f in html.split("<img")
                    if ' width=' in f]) == 4
        assert len([f for f in html.split("<img")
                    if ' height=' in f]) == 4

    def test_size_malformed1(self):
        text = u"""
<img src="/media/img/%s>
""" % IMAGE_NAME
        html = self._generic_test_image(text)
        assert ' width="%d"' % IMAGE_SIZE[0] in html
        assert ' height="%d"' % IMAGE_SIZE[1] in html

    def test_size_malformed2(self):
        text = u"""
<img src="/media/img/%s alt="hello">
""" % IMAGE_NAME
        html = self._generic_test_image(text)
        assert ' width="%d"' % IMAGE_SIZE[0] in html
        assert ' height="%d"' % IMAGE_SIZE[1] in html

    def test_outside_media_url(self):
        self.site.config.media_url = "http://media.example.com/"
        text = u"""
<img src="http://media.example.com/img/%s" alt="hello">
""" % IMAGE_NAME
        html = self._generic_test_image(text)
        assert ' width="%d"' % IMAGE_SIZE[0] in html
        assert ' height="%d"' % IMAGE_SIZE[1] in html
