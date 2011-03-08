# -*- coding: utf-8 -*-
"""
Syntext plugin
"""

from hyde.plugin import TextyPlugin

class SyntextPlugin(TextyPlugin):
    """
    The plugin class for syntax text replacement.
    """
    def __init__(self, site):
        super(SyntextPlugin, self).__init__(site)

    @property
    def tag_name(self):
        """
        The syntax tag.
        """
        return 'syntax'

    @property
    def default_open_pattern(self):
        """
        The default pattern for block open text.
        """
        return '^\s*~~~+\s*([A-Za-z0-9_\-\.:\']+)\s*~*\s*$'

    @property
    def default_close_pattern(self):
        """
        The default pattern for block close text.
        """
        return '^\s*~~~+\s*$'


    def get_params(self, match, start=True):
        """
        ~~~css~~~ will return css
        ~~~css/style.css will return css,style.css
        """
        params = super(SyntextPlugin, self).get_params(match, start)
        if ':' in params:
            (lex, _, filename) = params.rpartition(':')
            params = 'lex=\'%(lex)s\',filename=\'%(filename)s\'' % locals()
        return params

    def text_to_tag(self, match, start=True):
        """
        Replace open pattern (default:~~~~~css~~~~~~)
        with
        {% syntax css %} or equivalent and
        Replace close pattern (default: ~~~~~~)
        with
        {% endsyntax %} or equivalent
        """
        return super(SyntextPlugin, self).text_to_tag(match, start)
