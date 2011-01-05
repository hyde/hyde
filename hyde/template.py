# -*- coding: utf-8 -*-
# pylint: disable-msg=W0104,E0602,W0613,R0201
"""
Abstract classes and utilities for template engines
"""
from hyde.exceptions import HydeException

class Template(object):
    """
    Interface for hyde template engines. To use a different template engine,
    the following interface must be implemented.
    """

    def __init__(self, sitepath):
        self.sitepath = sitepath

    def configure(self, config):
        """
        The config object is a simple YAML object with required settings. The
        template implementations are responsible for transforming this object
        to match the `settings` required for the template engines.
        """

        abstract

    def render(self, text, context):
        """
        Given the text, and the context, this function must return the
        rendered string.
        """

        abstract

    @property
    def exception_class(self):
        return HydeException

    def get_include_statement(self, path_to_include):
        """
        Returns a include statement for the current template,
        given the path to include.
        """
        return "{%% include '%s' %%}" % path_to_include

    def get_block_open_statement(self, block_name):
        """
        Returns a open block statement for the current template,
        given the block name.
        """
        return "{%% block %s %%}" % block_name

    def get_block_close_statement(self, block_name):
        """
        Returns a close block statement for the current template,
        given the block name.
        """
        return "{%% endblock %s %%}" % block_name

    @staticmethod
    def find_template(site):
        """
        Reads the configuration to find the appropriate template.
        """
        # TODO: Find the appropriate template environment
        from hyde.ext.templates.jinja import Jinja2Template
        template = Jinja2Template(site.sitepath)
        return template
