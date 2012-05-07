# -*- coding: utf-8 -*-
"""
Text processing plugins
"""

from hyde.plugin import Plugin,TextyPlugin


#
# Blockdown
#

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


#
# Mark Text
#

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
        return u'^§§+\s*/([A-Za-z0-9_\-]*)\s*$'

    def text_to_tag(self, match, start=True):
        """
        Replace open pattern (default:§§ CSS)
        with
        {% mark CSS %} or equivalent and
        Replace close pattern (default: §§ /CSS)
        with
        {% endmark %} or equivalent
        """
        return super(MarkingsPlugin, self).text_to_tag(match, start)


#
# Reference Text
#

class ReferencePlugin(TextyPlugin):
    """
    The plugin class for reference text replacement.
    """
    def __init__(self, site):
        super(ReferencePlugin, self).__init__(site)

    @property
    def tag_name(self):
        """
        The refer tag.
        """
        return 'refer to'

    @property
    def default_open_pattern(self):
        """
        The default pattern for mark open text.
        """
        return u'^※\s*([^\s]+)\s*as\s*([A-Za-z0-9_\-]+)\s*$'

    @property
    def default_close_pattern(self):
        """
        No close pattern.
        """
        return None

    def text_to_tag(self, match, start=True):
        """
        Replace open pattern (default: ※ inc.md as inc)
        with
        {% refer to "inc.md" as inc %} or equivalent.
        """
        if not match.lastindex:
            return ''
        params = '"%s" as %s' % (match.groups(1)[0], match.groups(1)[1])
        return self.template.get_open_tag(self.tag_name, params)


#
# Syntax Text
#

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


#
# Text Links
#

class TextlinksPlugin(Plugin):
    """
    The plugin class for text link replacement.
    """
    def __init__(self, site):
        super(TextlinksPlugin, self).__init__(site)
        import re
        self.content_link = re.compile('\[\[([^\]^!][^\]]*)\]\]',
                                       re.UNICODE|re.MULTILINE)
        self.media_link = re.compile('\[\[\!\!([^\]]*)\]\]',
                                     re.UNICODE|re.MULTILINE)

    def begin_text_resource(self, resource, text):
        """
        Replace content url pattern [[/abc/def]])
        with
        {{ content_url('/abc/def') }} or equivalent and
        Replace media url pattern [[!!/abc/def]]
        with
        {{ media_url('/abc/def') }} or equivalent.
        """
        if not resource.uses_template:
            return text
        def replace_content(match):
            return self.template.get_content_url_statement(match.groups(1)[0])
        def replace_media(match):
            return self.template.get_media_url_statement(match.groups(1)[0])
        text = self.content_link.sub(replace_content, text)
        text = self.media_link.sub(replace_media, text)
        return text

