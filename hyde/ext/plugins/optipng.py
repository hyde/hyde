# -*- coding: utf-8 -*-
"""
OPTIPNG plugin
"""

from hyde.plugin import CLTransformer
from hyde.fs import File

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
