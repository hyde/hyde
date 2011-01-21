# -*- coding: utf-8 -*-
# pylint: disable-msg=W0104,E0602,W0613,R0201
"""
Abstract classes and utilities for template engines
"""
from hyde.exceptions import HydeException
from hyde.util import getLoggerWithNullHandler

class HtmlWrap(object):
    """
    A wrapper class for raw html.

    Provides pyquery interface if available.
    Otherwise raw html access.
    """

    def __init__(self, html):
        super(HtmlWrap, self).__init__()
        self.raw = html
        try:
            from pyquery import PyQuery
        except:
            PyQuery = False
        if PyQuery:
            self.q = PyQuery(html)

    def __unicode__(self):
        return self.raw

    def __call__(self, selector=None):
        if not self.q:
            return self.raw
        return self.q(selector).html()

class Template(object):
    """
    Interface for hyde template engines. To use a different template engine,
    the following interface must be implemented.
    """

    def __init__(self, sitepath):
        self.sitepath = sitepath
        self.logger = getLoggerWithNullHandler(self.__class__.__name__)

    def configure(self, site, engine):
        """
        The site object should contain a config attribute. The config object is
        a simple YAML object with required settings. The template implementations
        are responsible for transforming this object to match the `settings`
        required for the template engines.

        The engine is an informal protocol to provide access to some
        hyde internals.

        The preprocessor and postprocessor attributes must contain the
        functions that trigger the hyde plugins to preprocess the template
        after load and postprocess it after it is processed and code is generated.

        Note that the processors must only be used when referencing templates,
        for example, using the include tag. The regular preprocessing and
        post processing logic is handled by hyde.

        A context_for_path attribute must contain the function that returns the
        context object that is populated with the appropriate variables for the given
        path.
        """
        abstract

    def get_dependencies(self, text):
        """
        Finds the dependencies based on the included
        files.
        """
        return None

    def render(self, text, context):
        """
        Given the text, and the context, this function must return the
        rendered string.
        """

        abstract

    @property
    def exception_class(self):
        return HydeException

    @property
    def include_pattern(self):
        """
        The pattern for matching include statements
        """

        return '\s*\{\%\s*include\s*(?:\'|\")(.+?\.[^.]*)(?:\'|\")\s*\%\}'

    def get_include_statement(self, path_to_include):
        """
        Returns an include statement for the current template,
        given the path to include.
        """
        return "{%% include '%s' %%}" % path_to_include

    @property
    def block_open_pattern(self):
        """
        The pattern for matching include statements
        """

        return '\s*\{\%\s*block\s*([^\s]+)\s*\%\}'

    @property
    def block_close_pattern(self):
        """
        The pattern for matching include statements
        """

        return '\s*\{\%\s*endblock\s*([^\s]*)\s*\%\}'

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

    @property
    def extends_pattern(self):
        """
        The pattern for matching include statements
        """

        return '\s*\{\%\s*extends\s*(?:\'|\")(.+?\.[^.]*)(?:\'|\")\s*\%\}'

    def get_extends_statement(self, path_to_extend):
        """
        Returns an extends statement for the current template,
        given the path to extend.
        """
        return "{%% extends '%s' %%}" % path_to_extend

    @staticmethod
    def find_template(site):
        """
        Reads the configuration to find the appropriate template.
        """
        # TODO: Find the appropriate template environment
        from hyde.ext.templates.jinja import Jinja2Template
        template = Jinja2Template(site.sitepath)
        return template
