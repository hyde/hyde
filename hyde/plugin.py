# -*- coding: utf-8 -*-
"""
Contains definition for a plugin protocol and other utiltities.
"""


class Plugin(object):
    """
    The plugin protocol
    """

    def __init__(self, site):
        super(Plugin, self).__init__()
        self.site = site

    def template_loaded(self, template):
        """
        Called when the template for the site has been identified.
        """
        pass

    def prepare_site(self):
        """
        Called when generation is about to take place.
        """
        pass

    def site_load_complete(self):
        """
        Called when the site is built complete. This implies that all the
        nodes and resources have been identified and are accessible in the
        site variable.
        """
        pass

    def prepare_node(self, node):
        """
        Called when a node is about to be processed for generation.
        """
        pass

    def prepare_resource(self, resource, text):
        """
        Called when a resource is about to be processed for generation.
        The `text` parameter contains the, resource text at this point
        in its lifecycle. It is the text that has been loaded and any
        plugins that are higher in the order may have tampered with it.
        But the text has not been processed by the template yet.

        If this function returns a value, it is used as the text for further
        processing.
        """
        return text

    def process_resource(self, resource, text):
        """
        Called when a resource has been processed by the template.
        The `text` parameter contains the, resource text at this point
        in its lifecycle. It is the text that has been processed by the
        template and any plugins that are higher in the order may have
        tampered with it.

        If this function returns a value, it is used as the text for further
        processing.
        """
        return text

    def node_complete(self, node):
        """
        Called when all the resources in the node have been processed.
        """
        pass

    def site_complete(self):
        """
        Called when the entire site has been processed.
        """
        pass
