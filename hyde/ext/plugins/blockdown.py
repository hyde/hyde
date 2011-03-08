# -*- coding: utf-8 -*-
"""
Blockdown plugin
"""

from hyde.plugin import TextyPlugin

class BlockdownPlugin(TextyPlugin):
    """
    The plugin class for block text replacement.
    """
    def __init__(self, site):
        super(BlockdownPlugin, self).__init__(site)

    @property
    def tag_name(self):
        """
        The block tag.
        """
        return 'block'

    @property
    def default_open_pattern(self):
        """
        The default pattern for block open text.
        """
        return '^\s*===+([A-Za-z0-9_\-\.]+)=*\s*$'

    @property
    def default_close_pattern(self):
        """
        The default pattern for block close text.
        """
        return '^\s*===+/+\s*=*/*([A-Za-z0-9_\-\.]*)[\s=/]*$'

    def text_to_tag(self, match, start=True):
        """
        Replace open pattern (default:===[====]blockname[===========])
        with
        {% block blockname %} or equivalent and
        Replace close pattern (default===[====]/[blockname][===========])
        with
        {% endblock blockname %} or equivalent
        """
        return super(BlockdownPlugin, self).text_to_tag(match, start)