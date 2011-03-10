# -*- coding: utf-8 -*-
"""
Autoextend plugin
"""

from hyde.plugin import Plugin
import re

class AutoExtendPlugin(Plugin):
    """
    The plugin class for extending templates using metadata.
    """

    def __init__(self, site):
        super(AutoExtendPlugin, self).__init__(site)

    def begin_text_resource(self, resource, text):
        """
        If the meta data for the resource contains a layout attribute,
        and there is no extends statement, this plugin automatically adds
        an extends statement to the top of the file.
        """

        if not resource.uses_template:
            return text

        layout = None
        block = None
        try:
            layout = resource.meta.extends
        except AttributeError:
            pass

        try:
            block = resource.meta.default_block
        except AttributeError:
            pass

        if layout:
            self.logger.debug("Autoextending %s with %s" % (
                resource.relative_path, layout))
            extends_pattern = self.template.patterns['extends']

            if not re.search(extends_pattern, text):
                extended_text = self.template.get_extends_statement(layout)
                extended_text += '\n'
                if block:
                    extended_text += ('%s\n%s\n%s' %
                                        (self.t_block_open_tag(block),
                                            text,
                                            self.t_block_close_tag(block)))
                else:
                    extended_text += text
                return extended_text
        return text