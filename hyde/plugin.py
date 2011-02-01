# -*- coding: utf-8 -*-
"""
Contains definition for a plugin protocol and other utiltities.
"""
import abc
from hyde import loader

from hyde.util import getLoggerWithNullHandler
from functools import partial


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
        self.logger = getLoggerWithNullHandler(self.__class__.__name__)


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

    def raise_event(self, event_name):
        return getattr(Plugin.proxy, event_name)()

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
        return PluginProxy(site)
