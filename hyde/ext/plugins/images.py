# -*- coding: utf-8 -*-
"""
Contains classes to handle images related things

# Requires PIL or pillow
"""

from hyde.plugin import CLTransformer, Plugin


import glob
import os
import re

from fswrap import File

from hyde.exceptions import HydeException


class PILPlugin(Plugin):

    def __init__(self, site):
        super(PILPlugin, self).__init__(site)
        try:
            from PIL import Image
        except ImportError:
            # No pillow
            try:
                import Image
            except ImportError, e:
                raise HydeException('Unable to load PIL: ' + e.message)

        self.Image = Image


#
# Image sizer
#


class ImageSizerPlugin(PILPlugin):

    """
    Each HTML page is modified to add width and height for images if
    they are not already specified.

    # Requires PIL
    """

    def __init__(self, site):
        super(ImageSizerPlugin, self).__init__(site)
        self.cache = {}

    def _handle_img(self, resource, src, width, height):
        """Determine what should be added to an img tag"""
        if height is not None and width is not None:
            return ""           # Nothing
        if src is None:
            self.logger.warn(
                "[%s] has an img tag without src attribute" % resource)
            return ""           # Nothing
        if src not in self.cache:
            if src.startswith(self.site.config.media_url):
                path = src[len(self.site.config.media_url):].lstrip("/")
                path = self.site.config.media_root_path.child(path)
                image = self.site.content.resource_from_relative_deploy_path(
                    path)
            elif re.match(r'([a-z]+://|//).*', src):
                # Not a local link
                return ""       # Nothing
            elif src.startswith("/"):
                # Absolute resource
                path = src.lstrip("/")
                image = self.site.content.resource_from_relative_deploy_path(
                    path)
            else:
                # Relative resource
                path = resource.node.source_folder.child(src)
                image = self.site.content.resource_from_path(path)
            if image is None:
                self.logger.warn(
                    "[%s] has an unknown image" % resource)
                return ""       # Nothing
            if image.source_file.kind not in ['png', 'jpg', 'jpeg', 'gif']:
                self.logger.warn(
                    "[%s] has an img tag not linking to an image" % resource)
                return ""       # Nothing
            # Now, get the size of the image
            try:
                self.cache[src] = self.Image.open(image.path).size
            except IOError:
                self.logger.warn(
                    "Unable to process image [%s]" % image)
                self.cache[src] = (None, None)
                return ""       # Nothing
            self.logger.debug("Image [%s] is %s" % (src,
                                                    self.cache[src]))
        new_width, new_height = self.cache[src]
        if new_width is None or new_height is None:
            return ""           # Nothing
        if width is not None:
            return 'height="%d" ' % (int(width) * new_height / new_width)
        elif height is not None:
            return 'width="%d" ' % (int(height) * new_width / new_height)
        return 'height="%d" width="%d" ' % (new_height, new_width)

    def text_resource_complete(self, resource, text):
        """
        When the resource is generated, search for img tag and specify
        their sizes.

        Some img tags may be missed, this is not a perfect parser.
        """
        try:
            mode = self.site.config.mode
        except AttributeError:
            mode = "production"

        if not resource.source_file.kind == 'html':
            return

        if mode.startswith('dev'):
            self.logger.debug("Skipping sizer in development mode.")
            return

        pos = 0                 # Position in text
        img = None              # Position of current img tag
        state = "find-img"
        while pos < len(text):
            if state == "find-img":
                img = text.find("<img", pos)
                if img == -1:
                    break           # No more img tag
                pos = img + len("<img")
                if not text[pos].isspace():
                    continue        # Not an img tag
                pos = pos + 1
                tags = {"src": "",
                        "width": "",
                        "height": ""}
                state = "find-attr"
                continue
            if state == "find-attr":
                if text[pos] == ">":
                    # We get our img tag
                    insert = self._handle_img(resource,
                                              tags["src"] or None,
                                              tags["width"] or None,
                                              tags["height"] or None)
                    img = img + len("<img ")
                    text = "".join([text[:img], insert, text[img:]])
                    state = "find-img"
                    pos = pos + 1
                    continue
                attr = None
                for tag in tags:
                    if text[pos:(pos + len(tag) + 1)] == ("%s=" % tag):
                        attr = tag
                        pos = pos + len(tag) + 1
                        break
                if not attr:
                    pos = pos + 1
                    continue
                if text[pos] in ["'", '"']:
                    pos = pos + 1
                state = "get-value"
                continue
            if state == "get-value":
                if text[pos] == ">":
                    state = "find-attr"
                    continue
                if text[pos] in ["'", '"'] or text[pos].isspace():
                    # We got our value
                    pos = pos + 1
                    state = "find-attr"
                    continue
                tags[attr] = tags[attr] + text[pos]
                pos = pos + 1
                continue

        return text


def scale_aspect(a, b1, b2):
    from math import ceil
    """
  Scales a by b2/b1 rounding up to nearest integer
  """
    return int(ceil(a * b2 / float(b1)))


def thumb_scale_size(orig_width, orig_height, width, height):
    """
    Determine size to scale to scale for thumbnailst Params

    Params:
      orig_width, orig_height: original image dimensions
      width, height: thumbnail dimensions
    """
    if width is None:
        width = scale_aspect(orig_width, orig_height, height)
    elif height is None:
        height = scale_aspect(orig_height, orig_width, width)
    elif orig_width * height >= orig_height * width:
        width = scale_aspect(orig_width, orig_height, height)
    else:
        height = scale_aspect(orig_height, orig_width, width)

    return width, height

#
# Image Thumbnails
#


class ImageThumbnailsPlugin(PILPlugin):

    """
    Provide a function to get thumbnail for any image resource.

    Example of usage:
    Setting optional defaults in site.yaml:
        thumbnails:
          width: 100
          height: 120
          prefix: thumbnail_

    Setting thumbnails options in nodemeta.yaml:
        thumbnails:
          - width: 50
            prefix: thumbs1_
            include:
            - '*.png'
            - '*.jpg'
          - height: 100
            prefix: thumbs2_
            include:
            - '*.png'
            - '*.jpg'
          - larger: 100
            prefix: thumbs3_
            include:
            - '*.jpg'
          - smaller: 50
            prefix: thumbs4_
            include:
            - '*.jpg'
    which means - make four thumbnails from every picture with different
    prefixes and sizes

    It is only valid to specify either width/height or larger/smaller, but
    not to mix the two types.

    If larger/smaller are specified, then the orientation (i.e., landscape or
    portrait) is preserved while thumbnailing.

    If both width and height (or both larger and smaller) are defined, the
    image is cropped. You can define crop_type as one of these values:
    "topleft", "center" and "bottomright".  "topleft" is default.
    """

    def __init__(self, site):
        super(ImageThumbnailsPlugin, self).__init__(site)

    def thumb(self, resource, width, height, prefix, crop_type,
              preserve_orientation=False):
        """
        Generate a thumbnail for the given image
        """
        name = os.path.basename(resource.get_relative_deploy_path())
        # don't make thumbnails for thumbnails
        if name.startswith(prefix):
            return
        # Prepare path, make all thumnails in single place(content/.thumbnails)
        # for simple maintenance but keep original deploy path to preserve
        # naming logic in generated site
        path = os.path.join(".thumbnails",
                            os.path.dirname(
                                resource.get_relative_deploy_path()),
                            "%s%s" % (prefix, name))
        target = resource.site.config.content_root_path.child_file(path)
        res = self.site.content.add_resource(target)
        res.set_relative_deploy_path(
            res.get_relative_deploy_path().replace('.thumbnails/', '', 1))

        target.parent.make()
        if (os.path.exists(target.path) and os.path.getmtime(resource.path) <=
                os.path.getmtime(target.path)):
            return
        self.logger.debug("Making thumbnail for [%s]" % resource)

        im = self.Image.open(resource.path)
        if im.mode != 'RGBA':
            im = im.convert('RGBA')
        format = im.format

        if preserve_orientation and im.size[1] > im.size[0]:
            width, height = height, width

        resize_width, resize_height = thumb_scale_size(
            im.size[0], im.size[1], width, height)

        self.logger.debug("Resize to: %d,%d" % (resize_width, resize_height))
        im = im.resize((resize_width, resize_height), self.Image.ANTIALIAS)
        if width is not None and height is not None:
            shiftx = shifty = 0
            if crop_type == "center":
                shiftx = (im.size[0] - width) / 2
                shifty = (im.size[1] - height) / 2
            elif crop_type == "bottomright":
                shiftx = (im.size[0] - width)
                shifty = (im.size[1] - height)
            im = im.crop((shiftx, shifty, width + shiftx, height + shifty))
            im.load()

        options = dict(optimize=True)
        if format == "JPEG":
            options['quality'] = 75

        im.save(target.path, **options)

    def begin_site(self):
        """
        Find any image resource that should be thumbnailed and call thumb
        on it.
        """
        # Grab default values from config
        config = self.site.config
        defaults = {"width": None,
                    "height": None,
                    "larger": None,
                    "smaller": None,
                    "crop_type": "topleft",
                    "prefix": 'thumb_'}
        if hasattr(config, 'thumbnails'):
            defaults.update(config.thumbnails)

        for node in self.site.content.walk():
            if hasattr(node, 'meta') and hasattr(node.meta, 'thumbnails'):
                for th in node.meta.thumbnails:
                    if not hasattr(th, 'include'):
                        self.logger.error(
                            "Include is not set for node [%s]" % node)
                        continue
                    include = th.include
                    prefix = th.prefix if hasattr(
                        th, 'prefix') else defaults['prefix']
                    height = th.height if hasattr(
                        th, 'height') else defaults['height']
                    width = th.width if hasattr(
                        th, 'width') else defaults['width']
                    larger = th.larger if hasattr(
                        th, 'larger') else defaults['larger']
                    smaller = th.smaller if hasattr(
                        th, 'smaller') else defaults['smaller']
                    crop_type = th.crop_type if hasattr(
                        th, 'crop_type') else defaults['crop_type']
                    if crop_type not in ["topleft", "center", "bottomright"]:
                        self.logger.error(
                            "Unknown crop_type defined for node [%s]" % node)
                        continue
                    if (width is None and height is None and larger is None and
                            smaller is None):
                        self.logger.error(
                            "At least one of width, height, larger, or smaller"
                            "must be set for node [%s]" % node)
                        continue

                    if ((larger is not None or smaller is not None) and
                            (width is not None or height is not None)):
                        self.logger.error(
                            "It is not valid to specify both one of"
                            "width/height and one of larger/smaller"
                            "for node [%s]" % node)
                        continue

                    if larger is None and smaller is None:
                        preserve_orientation = False
                        dim1, dim2 = width, height
                    else:
                        preserve_orientation = True
                        dim1, dim2 = larger, smaller

                    def match_includes(s):
                        return any([glob.fnmatch.fnmatch(s, inc)
                                    for inc in include])

                    for resource in node.resources:
                        if match_includes(resource.path):
                            self.thumb(
                                resource, dim1, dim2, prefix, crop_type,
                                preserve_orientation)

#
# JPEG Optimization
#


class JPEGOptimPlugin(CLTransformer):

    """
    The plugin class for JPEGOptim
    """

    def __init__(self, site):
        super(JPEGOptimPlugin, self).__init__(site)

    @property
    def plugin_name(self):
        """
        The name of the plugin.
        """
        return "jpegoptim"

    def binary_resource_complete(self, resource):
        """
        If the site is in development mode, just return.
        Otherwise, run jpegoptim to compress the jpg file.
        """

        try:
            mode = self.site.config.mode
        except AttributeError:
            mode = "production"

        if not resource.source_file.kind == 'jpg':
            return

        if mode.startswith('dev'):
            self.logger.debug("Skipping jpegoptim in development mode.")
            return

        supported = [
            "force",
            "max=",
            "strip-all",
            "strip-com",
            "strip-exif",
            "strip-iptc",
            "strip-icc",
        ]
        target = File(self.site.config.deploy_root_path.child(
            resource.relative_deploy_path))
        jpegoptim = self.app
        args = [unicode(jpegoptim)]
        args.extend(self.process_args(supported))
        args.extend(["-q", unicode(target)])
        self.call_app(args)


class JPEGTranPlugin(CLTransformer):

    """
    Almost like jpegoptim except it uses jpegtran. jpegtran allows to make
    progressive JPEG. Unfortunately, it only does lossless compression. If
    you want both, you need to combine this plugin with jpegoptim one.
    """

    def __init__(self, site):
        super(JPEGTranPlugin, self).__init__(site)

    @property
    def plugin_name(self):
        """
        The name of the plugin.
        """
        return "jpegtran"

    def option_prefix(self, option):
        return "-"

    def binary_resource_complete(self, resource):
        """
        If the site is in development mode, just return.
        Otherwise, run jpegtran to compress the jpg file.
        """

        try:
            mode = self.site.config.mode
        except AttributeError:
            mode = "production"

        if not resource.source_file.kind == 'jpg':
            return

        if mode.startswith('dev'):
            self.logger.debug("Skipping jpegtran in development mode.")
            return

        supported = [
            "optimize",
            "progressive",
            "restart",
            "arithmetic",
            "perfect",
            "copy",
        ]
        source = File(self.site.config.deploy_root_path.child(
            resource.relative_deploy_path))
        target = File.make_temp('')
        jpegtran = self.app
        args = [unicode(jpegtran)]
        args.extend(self.process_args(supported))
        args.extend(["-outfile", unicode(target), unicode(source)])
        self.call_app(args)
        target.copy_to(source)
        target.delete()


#
# PNG Optimization
#

class OptiPNGPlugin(CLTransformer):

    """
    The plugin class for OptiPNG
    """

    def __init__(self, site):
        super(OptiPNGPlugin, self).__init__(site)

    @property
    def plugin_name(self):
        """
        The name of the plugin.
        """
        return "optipng"

    def option_prefix(self, option):
        return "-"

    def binary_resource_complete(self, resource):
        """
        If the site is in development mode, just return.
        Otherwise, run optipng to compress the png file.
        """

        try:
            mode = self.site.config.mode
        except AttributeError:
            mode = "production"

        if not resource.source_file.kind == 'png':
            return

        if mode.startswith('dev'):
            self.logger.debug("Skipping optipng in development mode.")
            return

        supported = [
            "o",
            "fix",
            "force",
            "preserve",
            "quiet",
            "log",
            "f",
            "i",
            "zc",
            "zm",
            "zs",
            "zw",
            "full",
            "nb",
            "nc",
            "np",
            "nz"
        ]
        target = File(self.site.config.deploy_root_path.child(
            resource.relative_deploy_path))
        optipng = self.app
        args = [unicode(optipng)]
        args.extend(self.process_args(supported))
        args.extend([unicode(target)])
        self.call_app(args)
