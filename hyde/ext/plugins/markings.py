# -*- coding: utf-8 -*-
"""
Markings plugin
"""

from hyde.ext.plugins.texty import TextyPlugin

class MarkingsPlugin(TextyPlugin):
    """
    The plugin class for mark text replacement.
    """
    def __init__(self, site):
        super(MarkingsPlugin, self).__init__(site)

    @property
    def tag_name(self):
        """
        The mark tag.
        """
        return 'mark'

    @property
    def default_open_pattern(self):
        """
        The default pattern for mark open text.
        """
        return u'^§§+\s*([A-Za-z0-9_\-]+)\s*$'

    @property
    def default_close_pattern(self):
        """
        The default pattern for mark close text.
        """
        return u'^§§+\s*([A-Za-z0-9_\-]*)\s*\.\s*$'

    def text_to_tag(self, match, start=True):
        """
        Replace open pattern (default:§§ CSS)
        with
        {% mark CSS %} or equivalent and
        Replace close pattern (default: §§ CSS.)
        with
        {% endmark %} or equivalent
        """
        text = super(MarkingsPlugin, self).text_to_tag(match, start)
        print text
        return text
