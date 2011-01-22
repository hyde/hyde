# -*- coding: utf-8 -*-
"""
Autoextend css plugin
"""

from hyde.plugin import Plugin

import re

class AutoExtendPlugin(Plugin):
    """
    The plugin class for less css
    """

    def __init__(self, site):
        super(AutoExtendPlugin, self).__init__(site)

    def template_loaded(self, template):
        self.template = template

    def begin_text_resource(self, resource, text):
        """
        If the meta data for the resource contains a layout attribute,
        and there is no extends statement, this plugin automatically adds
        an extends statement to the top of the file.
        """
        layout = None
        try:
            layout = resource.meta.extends
        except AttributeError:
            pass
        if layout:
            extends_pattern = self.template.patterns['extends']

            if not re.search(extends_pattern, text):
                extended_text = self.template.get_extends_statement(layout)
                extended_text += '\n'
                extended_text += text
                text = extended_text
        return text