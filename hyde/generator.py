"""
The generator class and related utility functions.
"""
from hyde.exceptions import HydeException
from hyde.fs import File, Folder
from hyde.plugin import Plugin
from hyde.template import Template

from contextlib import contextmanager

from hyde.util import getLoggerWithNullHandler
logger = getLoggerWithNullHandler('hyde.engine')


class Generator(object):
    """
    Generates output from a node or resource.
    """

    def __init__(self, site):
        super(Generator, self).__init__()
        self.site = site
        self.generated_once = False
        self.__context__ = dict(site=site)
        self.template = None
        Plugin.load_all(site)

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
                        res = None
                        if self.site.plugins:
                            for plugin in self.site.plugins:
                                if hasattr(plugin, method_name):
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
        self.events = PluginProxy(self.site)

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

    def load_template_if_needed(self):
        """
        Loads and configures the template environement from the site
        configuration if its not done already.
        """
        if not self.template:
            logger.info("Generating site at [%s]" % self.site.sitepath)
            self.template = Template.find_template(self.site)
            logger.debug("Using [%s] as the template",
                            self.template.__class__.__name__)

            logger.info("Configuring the template environment")
            self.template.configure(self.site,
                    preprocessor=self.events.begin_text_resource,
                    postprocessor=self.events.text_resource_complete)
            self.events.template_loaded(self.template)

    def initialize(self):
        """
        Start Generation. Perform setup tasks and inform plugins.
        """
        logger.info("Begin Generation")
        self.events.begin_generation()

    def load_site_if_needed(self):
        """
        Checks if the site requries a reload and loads if
        necessary.
        """
        #TODO: Perhaps this is better suited in Site
        if not len(self.site.content.child_nodes):
            logger.info("Reading site contents")
            self.site.load()

    def finalize(self):
        """
        Generation complete. Inform plugins and cleanup.
        """
        logger.info("Generation Complete")
        self.events.generation_complete()

    def has_resource_changed(self, resource):
        """
        Checks if the given resource has changed since the
        last generation.
        """
        self.load_site_if_needed()
        self.load_template_if_needed()
        target = File(self.site.config.deploy_root_path.child(
                                resource.relative_deploy_path))
        if not target.exists or target.older_than(resource.source_file):
            return True
        if resource.source_file.is_binary or not resource.uses_template:
            return False
        deps = self.template.get_dependencies(resource.source_file.read_all())
        if not deps or None in deps:
            return False
        content = self.site.content.source_folder
        layout = Folder(self.site.sitepath).child_folder('layout')
        for dep in deps:
            source = File(content.child(dep))
            if not source.exists:
                source = File(layout.child(dep))
            if not source.exists:
                return True
            if target.older_than(source):
                return True

        return False

    def generate_all(self):
        """
        Generates the entire website
        """
        logger.info("Reading site contents")
        self.load_template_if_needed()
        self.initialize()
        self.load_site_if_needed()
        self.events.begin_site()
        logger.info("Generating site to [%s]" %
                        self.site.config.deploy_root_path)
        self.__generate_node__(self.site.content)
        self.events.site_complete()
        self.finalize()
        self.generated_once = True

    def generate_node_at_path(self, node_path=None):
        """
        Generates a single node. If node_path is non-existent or empty,
        generates the entire site.
        """
        if not self.generated_once:
            return self.generate_all()
        self.load_template_if_needed()
        self.load_site_if_needed()
        node = None
        if node_path:
            node = self.site.content.node_from_path(node_path)
        self.generate_node(node)

    def generate_node(self, node=None):
        """
        Generates the given node. If node is invalid, empty or
        non-existent, generates the entire website.
        """
        if not node or not self.generated_once:
            return self.generate_all()

        self.load_template_if_needed()
        self.initialize()
        self.load_site_if_needed()

        try:
            self.__generate_node__(node)
            self.finalize()
        except HydeException:
            self.generate_all()

    def generate_resource_at_path(self, resource_path=None):
        """
        Generates a single resource. If resource_path is non-existent or empty,
        generats the entire website.
        """
        if not self.generated_once:
            return self.generate_all()

        self.load_template_if_needed()
        self.load_site_if_needed()
        resource = None
        if resource_path:
            resource = self.site.content.resource_from_path(resource_path)
        self.generate_resource(resource)

    def generate_resource(self, resource=None):
        """
        Generates the given resource. If resource is invalid, empty or
        non-existent, generates the entire website.
        """
        if not resource or not self.generated_once:
            return self.generate_all()

        self.load_template_if_needed()
        self.initialize()
        self.load_site_if_needed()

        try:
            self.__generate_resource__(resource)
            self.finalize()
        except HydeException:
            self.generate_all()


    def __generate_node__(self, node):
        for node in node.walk():
            logger.debug("Generating Node [%s]", node)
            self.events.begin_node(node)
            for resource in node.resources:
                self.__generate_resource__(resource)
            self.events.node_complete(node)

    def __generate_resource__(self, resource):
        if not resource.is_processable:
            logger.debug("Skipping [%s]", resource)
            return
        logger.debug("Processing [%s]", resource)
        with self.context_for_resource(resource) as context:
            if resource.source_file.is_text:
                text = resource.source_file.read_all()
                text = self.events.begin_text_resource(resource, text) or text
                if resource.uses_template:
                    logger.debug("Rendering [%s]", resource)
                    text = self.template.render(text, context)
                text = self.events.text_resource_complete(
                                        resource, text) or text
                target = File(self.site.config.deploy_root_path.child(
                                    resource.relative_deploy_path))
                target.parent.make()
                target.write(text)
            else:
                logger.debug("Copying binary file [%s]", resource)
                self.events.begin_binary_resource(resource)
                target = File(self.site.config.deploy_root_path.child(
                                    resource.relative_deploy_path))
                target.parent.make()
                resource.source_file.copy_to(target)
                self.events.binary_resource_complete(resource)
