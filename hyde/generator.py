"""
The generator class and related utility functions.
"""
from hyde.exceptions import HydeException
from hyde.fs import File
from hyde.template import Template

from contextlib import contextmanager

import logging
from logging import NullHandler

logger = logging.getLogger('hyde.engine')
logger.addHandler(NullHandler())


class Generator(object):
    """
    Generates output from a node or resource.
    """

    def __init__(self, site):
        super(Generator, self).__init__()
        self.site = site
        self.__context__ = dict(site=site)
        self.template = None

    @contextmanager
    def context_for_resource(self, resource):
        """
        Context manager that intializes the context for a given
        resource and rolls it back after the resource is processed.
        """
        # TODO: update metadata and other resource
        # specific properties here.
        self.__context__.update(resource=resource)
        yield self.__context__
        self.__context__.update(resource=None)

    def initialize_template_if_needed(self):
        """
        Loads and configures the template environement from the site
        configuration if its not done already.
        """
        if not self.template:
            logger.info("Generating site at [%s]" % self.site.sitepath)
            self.template = Template.find_template(self.site)
            logger.info("Using [%s] as the template", self.template)

            logger.info("Configuring the template environment")
            self.template.configure(self.site.config)

    def rebuild_if_needed(self):
        """
        Checks if the site requries a rebuild and builds if
        necessary.
        """
        #TODO: Perhaps this is better suited in Site
        if not len(self.site.content.child_nodes):
            logger.info("Reading site contents")
            self.site.build()

    def generate_all(self):
        """
        Generates the entire website
        """
        logger.info("Reading site contents")
        self.initialize_template_if_needed()
        self.rebuild_if_needed()

        logger.info("Generating site to [%s]" %
                        self.site.config.deploy_root_path)
        self.__generate_node__(self.site.content)

    def generate_node_at_path(self, node_path=None):
        """
        Generates a single node. If node_path is non-existent or empty,
        generates the entire site.
        """
        self.initialize_template_if_needed()
        self.rebuild_if_needed()
        node = None
        if node_path:
            node = self.site.content.node_from_path(node_path)
        self.generate_node(node)

    def generate_node(self, node=None):
        """
        Generates the given node. If node is invalid, empty or
        non-existent, generates the entire website.
        """
        self.initialize_template_if_needed()
        self.rebuild_if_needed()
        if not node:
            return self.generate_all()
        try:
            self.__generate_node__(node)
        except HydeException:
            self.generate_all()

    def generate_resource_at_path(self, resource_path=None):
        """
        Generates a single resource. If resource_path is non-existent or empty,
        generats the entire website.
        """
        self.initialize_template_if_needed()
        self.rebuild_if_needed()
        resource = None
        if resource_path:
            resource = self.site.content.resource_from_path(resource_path)
        return self.generate_resource(resource)

    def generate_resource(self, resource=None):
        """
        Generates the given resource. If resource is invalid, empty or
        non-existent, generates the entire website.
        """
        self.initialize_template_if_needed()
        self.rebuild_if_needed()
        if not resource:
            return self.generate_all()
        try:
            self.__generate_resource__(resource)
        except HydeException:
            self.generate_all()

    def __generate_node__(self, node):
        logger.info("Generating [%s]", node)
        for resource in node.walk_resources():
            self.__generate_resource__(resource)

    def __generate_resource__(self, resource):
        logger.info("Processing [%s]", resource)
        with self.context_for_resource(resource) as context:
            target = File(resource.source_file.get_mirror(
                            self.site.config.deploy_root_path,
                            self.site.content.source_folder))
            target.parent.make()
            if resource.source_file.is_text:
                logger.info("Rendering [%s]", resource)
                text = self.template.render(resource.source_file.read_all(),
                                        context)
                target.write(text)
            else:
                logger.info("Copying binary file [%s]", resource)
                resource.source_file.copy_to(target)
