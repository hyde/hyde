# -*- coding: utf-8 -*-
"""
jpegoptim plugin
"""

from hyde.plugin import CLTransformer
from hyde.fs import File

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
