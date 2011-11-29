# -*- coding: utf-8 -*-
"""
Contains classes to handle images related things

# Requires PIL
"""

from hyde.plugin import Plugin
from hyde.fs import File, Folder

import re
import Image
import glob
import os

class ImageSizerPlugin(Plugin):
    """
    Each HTML page is modified to add width and height for images if
    they are not already specified.
    """

    def __init__(self, site):
        super(ImageSizerPlugin, self).__init__(site)
        self.cache = {}

    def _handle_img(self, resource, src, width, height):
        """Determine what should be added to an img tag"""
        if height is not None and width is not None:
            return ""           # Nothing
        if src is None:
            self.logger.warn("[%s] has an img tag without src attribute" % resource)
            return ""           # Nothing
        if src not in self.cache:
            if src.startswith(self.site.config.media_url):
                path = src[len(self.site.config.media_url):].lstrip("/")
                path = self.site.config.media_root_path.child(path)
                image = self.site.content.resource_from_relative_deploy_path(path)
            elif re.match(r'([a-z]+://|//).*', src):
                # Not a local link
                return ""       # Nothing
            elif src.startswith("/"):
                # Absolute resource
                path = src.lstrip("/")
                image = self.site.content.resource_from_relative_deploy_path(path)
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
                self.cache[src] = Image.open(image.path).size
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
            return 'height="%d" ' % (int(width)*new_height/new_width)
        elif height is not None:
            return 'width="%d" ' % (int(height)*new_width/new_height)
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
                    if text[pos:(pos+len(tag)+1)] == ("%s=" % tag):
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

class ImageThumbnailsPlugin(Plugin):
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
    which means - make from every picture two thumbnails with different prefixes
    and sizes

    If both width and height defined, image would be cropped, you can define
    crop_type as one of these values: "topleft", "center" and "bottomright".
    "topleft" is default.

    Currently, only supports PNG and JPG.
    """

    def __init__(self, site):
        super(ImageThumbnailsPlugin, self).__init__(site)

    def thumb(self, resource, width, height, prefix, crop_type):
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
                            os.path.dirname(resource.get_relative_deploy_path()),
                            "%s%s" % (prefix, name))
        target = File(Folder(resource.site.config.content_root_path).child(path))
        res = self.site.content.add_resource(target)
        res.set_relative_deploy_path(res.get_relative_deploy_path().replace('.thumbnails/', '', 1))

        target.parent.make()
        if os.path.exists(target.path) and os.path.getmtime(resource.path) <= os.path.getmtime(target.path):
            return
        self.logger.debug("Making thumbnail for [%s]" % resource)

        im = Image.open(resource.path)
        if im.mode != 'RGBA':
            im = im.convert('RGBA')
        resize_width = width
        resize_height = height
        if resize_width is None:
            resize_width = im.size[0]*height/im.size[1] + 1
        elif resize_height is None:
            resize_height = im.size[1]*width/im.size[0] + 1
        elif im.size[0]*height >= im.size[1]*width:
            resize_width = im.size[0]*height/im.size[1]
        else:
            resize_height = im.size[1]*width/im.size[0]

        im = im.resize((resize_width, resize_height), Image.ANTIALIAS)
        if width is not None and height is not None:
            shiftx = shifty = 0
            if crop_type == "center":
                shiftx = (im.size[0] - width)/2
                shifty = (im.size[1] - height)/2
            elif crop_type == "bottomright":
                shiftx = (im.size[0] - width)
                shifty = (im.size[1] - height)
            im = im.crop((shiftx, shifty, width + shiftx, height + shifty))
            im.load()

        if resource.name.endswith(".jpg"):
            im.save(target.path, "JPEG", optimize=True, quality=75)
        else:
            im.save(target.path, "PNG", optimize=True)

    def begin_site(self):
        """
        Find any image resource that should be thumbnailed and call thumb on it.
        """
        # Grab default values from config
        config = self.site.config
        defaults = { "width": None,
                     "height": None,
                     "crop_type": "topleft",
                     "prefix": 'thumb_'}
        if hasattr(config, 'thumbnails'):
            defaults.update(config.thumbnails)

        for node in self.site.content.walk():
            if hasattr(node, 'meta') and hasattr(node.meta, 'thumbnails'):
                for th in node.meta.thumbnails:
                    if not hasattr(th, 'include'):
                        self.logger.error("Include is not set for node [%s]" % node)
                        continue
                    include = th.include
                    prefix = th.prefix if hasattr(th, 'prefix') else defaults['prefix']
                    height = th.height if hasattr(th, 'height') else defaults['height']
                    width = th.width if hasattr(th, 'width') else defaults['width']
                    crop_type = th.crop_type if hasattr(th, 'crop_type') else defaults['crop_type']
                    if crop_type not in ["topleft", "center", "bottomright"]:
                        self.logger.error("Unknown crop_type defined for node [%s]" % node)
                        continue
                    if width is None and height is None:
                        self.logger.error("Both width and height are not set for node [%s]" % node)
                        continue
                    thumbs_list = []
                    for inc in include:
                        for path in glob.glob(node.path + os.sep + inc):
                            thumbs_list.append(path)
                    for resource in node.resources:
                        if resource.source_file.kind in ["jpg", "png"] and resource.path in thumbs_list:
                            self.thumb(resource, width, height, prefix, crop_type)
