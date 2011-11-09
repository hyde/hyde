# -*- coding: utf-8 -*-
"""
Uglify plugin
"""

from hyde.plugin import CLTransformer
from hyde.fs import File

class UglifyPlugin(CLTransformer):
    """
    The plugin class for Uglify JS
    """

    def __init__(self, site):
        super(UglifyPlugin, self).__init__(site)

    @property
    def executable_name(self):
        return "uglifyjs"

    @property
    def plugin_name(self):
        """
        The name of the plugin.
        """
        return "uglify"

    def text_resource_complete(self, resource, text):
        """
        If the site is in development mode, just return.
        Otherwise, save the file to a temporary place
        and run the uglify app. Read the generated file
        and return the text as output.
        """

        try:
            mode = self.site.config.mode
        except AttributeError:
            mode = "production"

        if not resource.source_file.kind == 'js':
            return

        if mode.startswith('dev'):
            self.logger.debug("Skipping uglify in development mode.")
            return

        supported = [
            ("beautify", "b"),
            ("indent", "i"),
            ("quote-keys", "q"),
            ("mangle-toplevel", "mt"),
            ("no-mangle", "nm"),
            ("no-squeeze", "ns"),
            "no-seqs",
            "no-dead-code",
            ("no-copyright", "nc"),
            "overwrite",
            "verbose",
            "unsafe",
            "max-line-len",
            "reserved-names",
            "ascii"
        ]

        uglify = self.app
        source = File.make_temp(text)
        target = File.make_temp('')
        args = [unicode(uglify)]
        args.extend(self.process_args(supported))
        args.extend(["-o", unicode(target), unicode(source)])

        self.call_app(args)
        out = target.read_all()
        return out
