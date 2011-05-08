# -*- coding: utf-8 -*-
"""
Contains classes to handle images related things
"""

from hyde.plugin import Plugin

import re
import Image
from BeautifulSoup import BeautifulSoup

class ImageSizerPlugin(Plugin):
    """
    Each HTML page is modified to add width and height for images if
    they are not already specified.
    """

    def __init__(self, site):
        super(ImageSizerPlugin, self).__init__(site)
        self.cache = {}

    def text_resource_complete(self, resource, text):
        """
        When the resource is generated, search for img tag and specify
        their sizes.
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

        soup = BeautifulSoup(text)
        for img in soup.findAll('img'):
            if img.has_key('width') and img.has_key('height'):
                continue
            if not img.has_key('src'):
                self.logger.warn("[%s] has an img tag without src attribute" % resource)
                continue
            if not img['src'] in self.cache:
                if not re.match(r"(/[^/]|[^/]).*", img['src']):
                    # Not a local link
                    continue
                if img['src'].startswith("/"):
                    # Absolute resource
                    path = img['src'].lstrip("/")
                    image = self.site.content.resource_from_relative_deploy_path(path)
                else:
                    # Relative resource
                    path = resource.node.source_folder.child(img['src'])
                    image = self.site.content.resource_from_path(path)
                if image is None:
                    self.logger.warn(
                        "[%s] has an unknown image" % resource)
                    continue
                if image.source_file.kind not in ['png', 'jpg', 'jpeg', 'gif']:
                    self.logger.warn(
                        "[%s] has an img tag not linking to an image" % resource)
                    continue
                # Now, get the size of the image
                try:
                    self.cache[img['src']] = Image.open(image.path).size
                except IOError:
                    self.logger.warn(
                        "Unable to process image [%s]" % image)
                    self.cache[img['src']] = (None, None)
                    continue
                self.logger.debug("Image [%s] is %s" % (img['src'],
                                                        self.cache[img['src']]))
            width, height = self.cache[img['src']]
            if width is None:
                continue
            if img.has_key('width'):
                height = int(img['width'])*height/width
                width = int(img['width'])
            elif img.has_key('height'):
                width = int(img['height'])*width/height
                height = int(img['height'])
            img['height'], img['width'] = height, width
        return unicode(soup)
