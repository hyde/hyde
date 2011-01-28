# -*- coding: utf-8 -*-
"""
Provides classes and utilities that allow text
to be replaced before the templates are
rendered.
"""

from hyde.plugin import Plugin

import abc
import re
from functools import partial


class TextyPlugin(Plugin):
    """
    Base class for text preprocessing plugins.

    Plugins that desire to provide syntactic sugar for
    commonly used hyde functions for various templates
    can inherit from this class.
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, site):
        super(TextyPlugin, self).__init__(site)
        self.open_pattern = self.default_open_pattern
        self.close_pattern = self.default_close_pattern
        self.template = None
        config = getattr(site.config, self.plugin_name, None)

        if config and hasattr(config, 'open_pattern'):
            self.open_pattern = config.open_pattern

        if self.close_pattern and config and hasattr(config, 'close_pattern'):
            self.close_pattern = config.close_pattern

    @property
    def plugin_name(self):
        """
        The name of the plugin. Makes an intelligent guess.
        """
        return self.__class__.__name__.replace('Plugin', '').lower()

    @abc.abstractproperty
    def tag_name(self):
        """
        The tag that this plugin tries add syntactic sugar for.
        """
        return self.plugin_name

    @abc.abstractproperty
    def default_open_pattern(self):
        """
        The default pattern for opening the tag.
        """
        return None

    @abc.abstractproperty
    def default_close_pattern(self):
        """
        The default pattern for closing the tag.
        """
        return None

    def get_params(self, match, start=True):
        return match.groups(1)[0] if match.lastindex else ''

    @abc.abstractmethod
    def text_to_tag(self, match, start=True):
        """
        Replaces the matched text with tag statement
        given by the template.
        """
        params = self.get_params(match, start)
        return (self.template.get_open_tag(self.tag_name, params)
                if start
                else self.template.get_close_tag(self.tag_name, params))

    def begin_text_resource(self, resource, text):
        """
        Replace a text base pattern with a template statement.
        """
        text_open = re.compile(self.open_pattern, re.UNICODE|re.MULTILINE)
        text = text_open.sub(self.text_to_tag, text)
        if self.close_pattern:
            text_close = re.compile(self.close_pattern, re.UNICODE|re.MULTILINE)
            text = text_close.sub(
                    partial(self.text_to_tag, start=False), text)
        return text