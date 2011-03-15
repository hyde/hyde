# -*- coding: utf-8 -*-
"""
Contains definition for a plugin protocol and other utiltities.
"""
import abc

from hyde import loader

from hyde.exceptions import HydeException
from hyde.fs import File
from hyde.util import getLoggerWithNullHandler
from hyde.model import Expando

from functools import partial
import re
import subprocess
import traceback


logger = getLoggerWithNullHandler('hyde.engine')

class PluginProxy(object):
    """
    A proxy class to raise events in registered  plugins
    """

    def __init__(self, site):
        super(PluginProxy, self).__init__()
        self.site = site

    def __getattr__(self, method_name):
        if hasattr(Plugin, method_name):
            def __call_plugins__(*args):
                # logger.debug("Calling plugin method [%s]", method_name)
                res = None
                if self.site.plugins:
                    for plugin in self.site.plugins:
                        if hasattr(plugin, method_name):
                            # logger.debug(
                            #    "\tCalling plugin [%s]",
                            #   plugin.__class__.__name__)
                            function = getattr(plugin, method_name)
                            res = function(*args)
                            if res:
                                targs = list(args)
                                last = None
                                if len(targs):
                                    last = targs.pop()
                                    targs.append(res if res else last)
                                args = tuple(targs)
                return res

            return __call_plugins__
        raise HydeException(
                "Unknown plugin method [%s] called." % method_name)

class Plugin(object):
    """
    The plugin protocol
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, site):
        super(Plugin, self).__init__()
        self.site = site
        self.logger = getLoggerWithNullHandler(
                            'hyde.engine.%s' % self.__class__.__name__)
        self.template = None


    def template_loaded(self, template):
        """
        Called when the template for the site has been identified.

        Handles the template loaded event to keep
        a reference to the template object.
        """
        self.template = template

    def __getattribute__(self, name):
        """
        Syntactic sugar for template methods
        """
        if name.startswith('t_') and self.template:
            attr = name[2:]
            if hasattr(self.template, attr):
                return self.template[attr]
            elif attr.endswith('_close_tag'):
                tag = attr.replace('_close_tag', '')
                return partial(self.template.get_close_tag, tag)
            elif attr.endswith('_open_tag'):
                tag = attr.replace('_open_tag', '')
                return partial(self.template.get_open_tag, tag)

        return super(Plugin, self).__getattribute__(name)

    def begin_generation(self):
        """
        Called when generation is about to take place.
        """
        pass

    def begin_site(self):
        """
        Called when the site is loaded completely. This implies that all the
        nodes and resources have been identified and are accessible in the
        site variable.
        """
        pass

    def begin_node(self, node):
        """
        Called when a node is about to be processed for generation.
        This method is called only when the entire node is generated.
        """
        pass

    def begin_text_resource(self, resource, text):
        """
        Called when a text resource is about to be processed for generation.
        The `text` parameter contains the resource text at this point
        in its lifecycle. It is the text that has been loaded and any
        plugins that are higher in the order may have tampered with it.
        But the text has not been processed by the template yet. Note that
        the source file associated with the text resource may not be modifed
        by any plugins.

        If this function returns a value, it is used as the text for further
        processing.
        """
        return text

    def begin_binary_resource(self, resource):
        """
        Called when a binary resource is about to be processed for generation.

        Plugins are free to modify the contents of the file.
        """
        pass

    def text_resource_complete(self, resource, text):
        """
        Called when a resource has been processed by the template.
        The `text` parameter contains the resource text at this point
        in its lifecycle. It is the text that has been processed by the
        template and any plugins that are higher in the order may have
        tampered with it. Note that the source file associated with the
        text resource may not be modifed by any plugins.

        If this function returns a value, it is used as the text for further
        processing.
        """
        return text

    def binary_resource_complete(self, resource):
        """
        Called when a binary resource has already been processed.

        Plugins are free to modify the contents of the file.
        """
        pass

    def node_complete(self, node):
        """
        Called when all the resources in the node have been processed.
        This method is called only when the entire node is generated.
        """
        pass

    def site_complete(self):
        """
        Called when the entire site has been processed. This method is called
        only when the entire site is generated.
        """
        pass

    def generation_complete(self):
        """
        Called when generation is completed.
        """
        pass

    @staticmethod
    def load_all(site):
        """
        Loads plugins based on the configuration. Assigns the plugins to
        'site.plugins'
        """
        site.plugins = [loader.load_python_object(name)(site)
                            for name in site.config.plugins]

    @staticmethod
    def get_proxy(site):
        """
        Returns a new instance of the Plugin proxy.
        """
        return PluginProxy(site)

class CLTransformer(Plugin):
    """
    Handy class for plugins that simply call a command line app to
    transform resources.
    """

    @property
    def plugin_name(self):
        """
        The name of the plugin. Makes an intelligent guess.
        """

        return self.__class__.__name__.replace('Plugin', '').lower()

    @property
    def defaults(self):
        """
        Default command line options. Can be overridden
        by specifying them in config.
        """

        return {}

    @property
    def executable_not_found_message(self):
        """
        Message to be displayed if the command line application
        is not found.
        """

        return ("%(name)s executable path not configured properly. "
        "This plugin expects `%(name)s.app` to point "
        "to the `%(name)s` executable." % {"name": self.plugin_name})

    @property
    def settings(self):
        """
        The settings for this plugin the site config.
        """

        opts = Expando({})
        try:
            opts = getattr(self.site.config, self.plugin_name)
        except AttributeError:
            pass
        return opts

    @property
    def app(self):
        """
        Gets the application path from the site configuration.
        """

        try:
            app_path = getattr(self.settings, 'app')
        except AttributeError:
            raise self.template.exception_class(
                    self.executable_not_found_message)

        app = File(app_path)

        if not app.exists:
            raise self.template.exception_class(
                    self.executable_not_found_message)

        return app

    def option_prefix(self, option):
        return "--"

    def process_args(self, supported):
        """
        Given a list of supported arguments, consutructs an argument
        list that could be passed on to the call_app function.
        """
        args = {}
        args.update(self.defaults)
        try:
            args.update(getattr(self.settings, 'args').to_dict())
        except AttributeError:
            pass

        result = []
        for arg in supported:
            if isinstance(arg, tuple):
                (descriptive, short) = arg
            else:
                descriptive = short = arg

            if descriptive in args or short in args:
                result.append("%s%s" % (self.option_prefix(descriptive),
                                        descriptive))
                val = args[descriptive if descriptive in args else short]
                if val:
                    result.append(val)
        return result

    def call_app(self, args):
        """
        Calls the application with the given command line parameters.
        """
        try:
            self.logger.debug(
                "Calling executable [%s] with arguments %s" %
                    (args[0], str(args[1:])))
            subprocess.check_call(args)
        except subprocess.CalledProcessError, error:
            self.logger.error(traceback.format_exc())
            self.logger.error(error.output)
            raise

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
        """
        Default implementation for getting template args.
        """
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