# -*- coding: utf-8 -*-
"""
Minifying resources.
"""

from hyde.plugin import Plugin

class HtmlMinPlugin(Plugin):
    """
    The plugin class for html minification
    Based upon http://htmlmin.readthedocs.org. See the docs for more info.
    Supported settings:
    extensions: list of file extensions to filter. By default: ['.html', ]
    All the parameters supported by the htmlmin library,
        e.g: "remove_comments: True".
    """
    def __init__(self, site):
        super(HtmlMinPlugin, self).__init__(site)
        import htmlmin

        # Filter out all the settings that are not relevant to htmlmin.
        module_settings = dict(self.settings)

        self.minifier = htmlmin.Minifier(**module_settings)

    def text_resource_complete(self, resource, text):
        """
        Minify after finishing with the text.
        """

        mode = getattr(self.site.config, 'mode', 'production')

        if mode.startswith('dev'):
            self.logger.debug("Skipping HtmlMin in development mode.")
            return

        if resource.source_file.kind != 'html':
            return

        return self.minifier.minify(text)
