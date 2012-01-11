# -*- coding: utf-8 -*-
"""
Interpret files `*.html.rst` as reStructuredText sources, `*.html.md`, as Markdown
and `*.html.tx` as Textile.

Replace content of a file by

    {% filter <filtername> %}
    ...
    {% endfilter %}

"""

from hyde.plugin import Plugin

from hyde.util import getLoggerWithNullHandler

logger = getLoggerWithNullHandler('hyde.ext.plugins.syntax')


class SyntaxPlugin(Plugin):
    """The plugin class for rendering sphinx-generated documentation."""

    extensions_map = {
        "rst": "restructuredtext",
        "md": "markdown",
        "tx": "textile"
    }
    extensions = [".html." + i for i in extensions_map.keys()]

    def __init__(self, site):
        self.generators = {}
        super(SyntaxPlugin, self).__init__(site)
        self.docsroot = self.settings.get("docsroot", "docs")

    def begin_text_resource(self, resource, text):
        """Event hook for processing an individual resource.

        If the input resource is a sphinx input file, this method will replace
        replace the text of the file with the sphinx-generated documentation.

        Sphinx itself is run lazily the first time this method is called.
        This means that if no sphinx-related resources need updating, then
        we entirely avoid running sphinx.
        """

        rel_path = resource.relative_path

        for i in self.extensions:
            if rel_path.endswith(i):
                return self.process_resource(resource, text)

        return text

    def process_resource(self, resource, text):
        logger.debug("Process `%s` resource", resource.relative_path)

        for ext, filter in self.extensions_map.items():
            if resource.relative_path.endswith(ext):
                deploy_path = resource.relative_path[:-(len(ext) + 1)]
                logger.debug("Set relative deploy path to `%s`", deploy_path)
                resource.relative_deploy_path = deploy_path
                logger.debug("Apply `%s` filter", filter)
                return ''.join([
                    "{% filter ", filter, " %}",
                    text,
                    "{% endfilter %}"
                ])

        raise RuntimeError("This error should never occurred if code is correct,"
                           " because this function is called only if file has right extension")
