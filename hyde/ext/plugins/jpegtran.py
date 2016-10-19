# -*- coding: utf-8 -*-
"""
jpegtran plugin

Almost like jpegoptim except it uses jpegtran. jpegtran allows to make
progressive JPEG. Unfortunately, it only does lossless compression. If
you want both, you need to combine this plugin with jpegoptim one.
"""

from hyde.plugin import CLTransformer
from hyde.fs import File

class JPEGTranPlugin(CLTransformer):
    """
    The plugin class for JPEGTran
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
