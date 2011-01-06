"""
Blockdown css plugin
"""

from hyde.plugin import Plugin
from hyde.fs import File, Folder

import re
from functools import partial

class BlockdownPlugin(Plugin):
    """
    The plugin class for less css
    """

    def __init__(self, site):
        super(BlockdownPlugin, self).__init__(site)
        try:
            self.open_pattern = site.config.blockdown.open_pattern
        except AttributeError:
            self.open_pattern = '^\s*===+\s*([A-Za-z0-9_\-.]+)\s*=*\s*$'

        try:
            self.close_pattern = site.config.blockdown.close_pattern
        except AttributeError:
            self.close_pattern = '^\s*===+\s*/+\s*=*/*([A-Za-z0-9_\-.]*)[\s=/]*$'

    def template_loaded(self, template):
        self.template = template

    def begin_text_resource(self, resource, text):
        """
        Replace open pattern (default:===[====]blockname[===========])
        with
        {% block blockname %} or equivalent and
        Replace close pattern (default===[====]/[blockname][===========])
        with
        {% block blockname %} or equivalent
        """
        blocktag_open = re.compile(self.open_pattern, re.MULTILINE)
        blocktag_close = re.compile(self.close_pattern, re.MULTILINE)
        def blockdown_to_block(match, start_block=True):
            if not match.lastindex:
                return ''
            block_name = match.groups(1)[0]
            return (self.template.get_block_open_statement(block_name)
                    if start_block
                    else self.template.get_block_close_statement(block_name))
        text = blocktag_open.sub(blockdown_to_block, text)
        text = blocktag_close.sub(partial(blockdown_to_block, start_block=False), text)
        return text