# -*- coding: utf-8 -*-
"""
Use nose
`$ pip install nose`
`$ nosetests`

Requires PIL
"""
from hyde.generator import Generator
from hyde.site import Site
from hyde.ext.plugins.images import thumb_scale_size


from fswrap import File
import yaml

TEST_SITE = File(__file__).parent.parent.child_folder('_test')
IMAGE_SOURCE = File(__file__).parent.child_folder('images')

PORTRAIT_IMAGE = "portrait.jpg"
PORTRAIT_SIZE = (90, 120)
LANDSCAPE_IMAGE = "landscape.jpg"
LANDSCAPE_SIZE = (120, 90)

IMAGES = [PORTRAIT_IMAGE, LANDSCAPE_IMAGE]
SIZES = [PORTRAIT_SIZE, LANDSCAPE_SIZE]

# PIL requirement
try:
    from PIL import Image
except ImportError:
    # No pillow
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
""" % PORTRAIT_IMAGE
        html = self._generic_test_image(text)
        assert ' width="%d"' % PORTRAIT_SIZE[0] in html
        assert ' height="%d"' % PORTRAIT_SIZE[1] in html

    def test_size_image_relative(self):
        text = u"""
<img src="media/img/%s">
""" % PORTRAIT_IMAGE
        html = self._generic_test_image(text)
        assert ' width="%d"' % PORTRAIT_SIZE[0] in html
        assert ' height="%d"' % PORTRAIT_SIZE[1] in html

    def test_size_image_no_resize(self):
        text = u"""
<img src="/media/img/%s" width="2000" height="150">
""" % PORTRAIT_IMAGE
        html = self._generic_test_image(text)
        assert ' width="%d"' % PORTRAIT_SIZE[0] not in html
        assert ' height="%d"' % PORTRAIT_SIZE[1] not in html

    def test_size_image_size_proportional(self):
        text = u"""
<img src="/media/img/%s" width="%d">
""" % (PORTRAIT_IMAGE,  PORTRAIT_SIZE[0]*2)
        html = self._generic_test_image(text)
        assert ' width="%d"' % (PORTRAIT_SIZE[0]*2) in html
        assert ' height="%d"' % (PORTRAIT_SIZE[1]*2) in html

    def test_size_image_not_exists(self):
        text = u"""
<img src="/media/img/hyde-logo-no.png">
"""
        self._generic_test_image(text)

    def test_size_image_multiline(self):
        text = u"""
     <img src="/media/img/%s">
""" % PORTRAIT_IMAGE
        html = self._generic_test_image(text)
        assert ' width="%d"' % PORTRAIT_SIZE[0] in html
        assert ' height="%d"' % PORTRAIT_SIZE[1] in html

    def test_size_multiple_images(self):
        text = u"""
<img src="/media/img/%s">
<img src="/media/img/%s">Hello <img src="/media/img/%s">
<img src="/media/img/%s">Bye
""" % ((PORTRAIT_IMAGE,)*4)
        html = self._generic_test_image(text)
        assert ' width="%d"' % PORTRAIT_SIZE[0] in html
        assert ' height="%d"' % PORTRAIT_SIZE[1] in html
        assert 'Hello ' in html
        assert 'Bye' in html
        assert len([f for f in html.split("<img")
                    if ' width=' in f]) == 4
        assert len([f for f in html.split("<img")
                    if ' height=' in f]) == 4

    def test_size_malformed1(self):
        text = u"""
<img src="/media/img/%s>
""" % PORTRAIT_IMAGE
        html = self._generic_test_image(text)
        assert ' width="%d"' % PORTRAIT_SIZE[0] in html
        assert ' height="%d"' % PORTRAIT_SIZE[1] in html

    def test_size_malformed2(self):
        text = u"""
<img src="/media/img/%s alt="hello">
""" % PORTRAIT_IMAGE
        html = self._generic_test_image(text)
        assert ' width="%d"' % PORTRAIT_SIZE[0] in html
        assert ' height="%d"' % PORTRAIT_SIZE[1] in html

    def test_outside_media_url(self):
        self.site.config.media_url = "http://media.example.com/"
        text = u"""
<img src="http://media.example.com/img/%s" alt="hello">
""" % PORTRAIT_IMAGE
        html = self._generic_test_image(text)
        assert ' width="%d"' % PORTRAIT_SIZE[0] in html
        assert ' height="%d"' % PORTRAIT_SIZE[1] in html

class TestImageThumbSize(object):

    def test_width_only(self):
        ow, oh = 100, 200
        nw, nh = thumb_scale_size(ow, oh, 50, None)
        assert nw == 50
        assert nh == 100

    def test_width_only_nonintegral(self):
        ow, oh = 100, 205
        nw, nh = thumb_scale_size(ow, oh, 50, None)
        assert nw == 50
        assert nh == 103

    def test_height_only(self):
        ow, oh = 100, 200
        nw, nh = thumb_scale_size(ow, oh, None, 100)
        assert nw == 50
        assert nh == 100

    def test_height_only_nonintegral(self):
        ow, oh = 105, 200
        nw, nh = thumb_scale_size(ow, oh, None, 100)
        assert nw == 53
        assert nh == 100

    def test_height_and_width_portrait(self):
        ow, oh = 100, 200
        nw, nh = thumb_scale_size(ow, oh, 50, 50)
        assert nw == 50
        assert nh == 100

    def test_height_and_width_landscape(self):
        ow, oh = 200, 100
        nw, nh = thumb_scale_size(ow, oh, 50, 50)
        assert nw == 100
        assert nh == 50

class TestImageThumbnails(object):
    # TODO: add tests for cropping? (not easy currently)

    def setUp(self):
        TEST_SITE.make()
        TEST_SITE.parent.child_folder(
                    'sites/test_jinja').copy_contents_to(TEST_SITE)
        IMAGES = TEST_SITE.child_folder('content/media/img')
        IMAGES.make()
        IMAGE_SOURCE.copy_contents_to(IMAGES)
        self.image_folder = IMAGES
        self.site = Site(TEST_SITE)

    def tearDown(self):
        TEST_SITE.delete()

    def _generate_site_with_meta(self, meta):
        self.site.config.mode = "production"
        self.site.config.plugins = ['hyde.ext.plugins.meta.MetaPlugin', 'hyde.ext.plugins.images.ImageThumbnailsPlugin']

        mlink = File(self.image_folder.child('meta.yaml'))
        meta_text = yaml.dump(meta, default_flow_style=False)
        mlink.write(meta_text)
        gen = Generator(self.site)
        gen.generate_all()

    def _test_generic_thumbnails(self, meta):
        self._generate_site_with_meta(meta)
        thumb_meta = meta.get('thumbnails', [])
        for th in thumb_meta:
            prefix = th.get('prefix')
            if prefix is None:
                continue

            for fn in [PORTRAIT_IMAGE, LANDSCAPE_IMAGE]:
                f = File(self._deployed_image(prefix, fn))
                assert f.exists

    def _deployed_image(self, prefix, filename):
        return self.site.config.deploy_root_path.child('media/img/%s%s'%(prefix,filename))

    def test_width(self):
        prefix='thumb_'
        meta = dict(thumbnails=[dict(width=50, prefix=prefix, include=['*.jpg'])])
        self._test_generic_thumbnails(meta)
        for fn in IMAGES:
            im = Image.open(self._deployed_image(prefix, fn))
            assert im.size[0] == 50

    def test_height(self):
        prefix='thumb_'
        meta = dict(thumbnails=[dict(height=50, prefix=prefix, include=['*.jpg'])])
        self._test_generic_thumbnails(meta)
        for fn in IMAGES:
            im = Image.open(self._deployed_image(prefix, fn))
            assert im.size[1] == 50

    def test_width_and_height(self):
        prefix='thumb_'
        meta = dict(thumbnails=[dict(width=50, height=50, prefix=prefix, include=['*.jpg'])])
        self._test_generic_thumbnails(meta)
        for fn in IMAGES:
            im = Image.open(self._deployed_image(prefix, fn))
            assert im.size[0] == 50
            assert im.size[1] == 50

    def test_larger(self):
        prefix='thumb_'
        meta = dict(thumbnails=[dict(larger=50, prefix=prefix, include=['*.jpg'])])
        self._test_generic_thumbnails(meta)

        im = Image.open(self._deployed_image(prefix, PORTRAIT_IMAGE))
        assert im.size[1] == 50

        im = Image.open(self._deployed_image(prefix, LANDSCAPE_IMAGE))
        assert im.size[0] == 50

    def test_smaller(self):
        prefix='thumb_'
        meta = dict(thumbnails=[dict(smaller=50, prefix=prefix, include=['*.jpg'])])
        self._test_generic_thumbnails(meta)

        im = Image.open(self._deployed_image(prefix, PORTRAIT_IMAGE))
        assert im.size[0] == 50

        im = Image.open(self._deployed_image(prefix, LANDSCAPE_IMAGE))
        assert im.size[1] == 50

    def test_larger_and_smaller(self):
        prefix='thumb_'
        meta = dict(thumbnails=[dict(larger=100, smaller=50, prefix=prefix, include=['*.jpg'])])
        self._test_generic_thumbnails(meta)

        im = Image.open(self._deployed_image(prefix, PORTRAIT_IMAGE))
        assert im.size[0] == 50
        assert im.size[1] == 100

        im = Image.open(self._deployed_image(prefix, LANDSCAPE_IMAGE))
        assert im.size[0] == 100
        assert im.size[1] == 50
