# -*- coding: utf-8 -*-
"""
Textlinks plugin
"""
import re

from hyde.plugin import Plugin

class TextlinksPlugin(Plugin):
    """
    The plugin class for syntax text replacement.
    """
    def __init__(self, site):
        super(TextlinksPlugin, self).__init__(site)

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
        content_link = re.compile('\[\[([^\]^!][^\]]*)\]\]', re.UNICODE|re.MULTILINE)
        media_link = re.compile('\[\[\!\!([^\]]*)\]\]', re.UNICODE|re.MULTILINE)
        def replace_content(match):
            return self.template.get_content_url_statement(match.groups(1)[0])
        def replace_media(match):
            return self.template.get_media_url_statement(match.groups(1)[0])
        text = content_link.sub(replace_content, text)
        text = media_link.sub(replace_media, text)
        return text