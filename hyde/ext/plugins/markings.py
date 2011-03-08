# -*- coding: utf-8 -*-
"""
Markings plugin
"""

from hyde.plugin import TextyPlugin

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