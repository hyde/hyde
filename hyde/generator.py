# -*- coding: utf-8 -*-
"""
The generator class and related utility functions.
"""

from commando.util import getLoggerWithNullHandler
from fswrap import File, Folder
from hyde.exceptions import HydeException
from hyde.model import Context, Dependents
from hyde.plugin import Plugin
from hyde.template import Template
from hyde.site import Resource

from contextlib import contextmanager
from datetime import datetime
from shutil import copymode
import sys

logger = getLoggerWithNullHandler('hyde.engine')


class Generator(object):
    """
    Generates output from a node or resource.
    """

    def __init__(self, site):
        super(Generator, self).__init__()
        self.site = site
        self.generated_once = False
        self.deps = Dependents(site.sitepath)
        self.waiting_deps = {}
        self.create_context()
        self.template = None
        Plugin.load_all(site)

        self.events = Plugin.get_proxy(self.site)

    def create_context(self):
        site = self.site
        self.__context__ = dict(site=site)
        if hasattr(site.config, 'context'):
            site.context = Context.load(site.sitepath, site.config.context)
            self.__context__.update(site.context)


    @contextmanager
    def context_for_resource(self, resource):
        """
        Context manager that intializes the context for a given
        resource and rolls it back after the resource is processed.
        """
        self.__context__.update(
            resource=resource,
            node=resource.node,
            time_now=datetime.now())
        yield self.__context__
        self.__context__.update(resource=None, node=None)

    def context_for_path(self, path):
        resource = self.site.resource_from_path(path)
        if not resource:
            return {}
        ctx = self.__context__.copy
        ctx.resource = resource
        return ctx

    def load_template_if_needed(self):
        """
        Loads and configures the template environement from the site
        configuration if its not done already.
        """

        class GeneratorProxy(object):
            """
            An interface to templates and plugins for
            providing restricted access to the methods.
            """

            def __init__(self, preprocessor=None, postprocessor=None, context_for_path=None):
                self.preprocessor = preprocessor
                self.postprocessor = postprocessor
                self.context_for_path = context_for_path

        if not self.template:
            logger.info("Generating site at [%s]" % self.site.sitepath)
            self.template = Template.find_template(self.site)
            logger.debug("Using [%s] as the template",
                            self.template.__class__.__name__)

            logger.info("Configuring the template environment")
            self.template.configure(self.site,
                        engine=GeneratorProxy(
                            context_for_path=self.context_for_path,
                            preprocessor=self.events.begin_text_resource,
                            postprocessor=self.events.text_resource_complete))
            self.events.template_loaded(self.template)

    def initialize(self):
        """
        Start Generation. Perform setup tasks and inform plugins.
        """
        logger.debug("Begin Generation")
        self.events.begin_generation()

    def load_site_if_needed(self):
        """
        Checks if the site requries a reload and loads if
        necessary.
        """
        self.site.reload_if_needed()

    def finalize(self):
        """
        Generation complete. Inform plugins and cleanup.
        """
        logger.debug("Generation Complete")
        self.events.generation_complete()

    def get_dependencies(self, resource):
        """
        Gets the dependencies for a given resource.
        """

        rel_path = resource.relative_path
        deps = self.deps[rel_path] if rel_path in self.deps \
                    else self.update_deps(resource)
        return deps

    def update_deps(self, resource):
        """
        Updates the dependencies for the given resource.
        """
        if not resource.source_file.is_text:
            return []
        rel_path = resource.relative_path
        self.waiting_deps[rel_path] = []
        deps = []
        if hasattr(resource, 'depends'):
            user_deps = resource.depends
            for dep in user_deps:
                deps.append(dep)
                dep_res = self.site.content.resource_from_relative_path(dep)
                if dep_res:
                    if dep_res.relative_path in self.waiting_deps.keys():
                        self.waiting_deps[dep_res.relative_path].append(rel_path)
                    else:
                        deps.extend(self.get_dependencies(dep_res))
        if resource.uses_template:
            deps.extend(self.template.get_dependencies(rel_path))
        deps = list(set(deps))
        if None in deps:
            deps.remove(None)
        self.deps[rel_path] = deps
        for path in self.waiting_deps[rel_path]:
            self.deps[path].extend(deps)
        return deps

    def has_resource_changed(self, resource):
        """
        Checks if the given resource has changed since the
        last generation.
        """
        logger.debug("Checking for changes in %s" % resource)
        self.load_template_if_needed()
        self.load_site_if_needed()

        target = File(self.site.config.deploy_root_path.child(
                                resource.relative_deploy_path))
        if not target.exists or target.older_than(resource.source_file):
            logger.debug("Found changes in %s" % resource)
            return True
        if resource.source_file.is_binary:
            logger.debug("No Changes found in %s" % resource)
            return False
        if self.site.config.needs_refresh() or \
           not target.has_changed_since(self.site.config.last_modified):
            logger.debug("Site configuration changed")
            return True

        deps = self.get_dependencies(resource)
        if not deps or None in deps:
            logger.debug("No changes found in %s" % resource)
            return False
        content = self.site.content.source_folder
        layout = Folder(self.site.sitepath).child_folder('layout')
        logger.debug("Checking for changes in dependents:%s" % deps)
        for dep in deps:
            if not dep:
                return True
            source = File(content.child(dep))
            if not source.exists:
                source = File(layout.child(dep))
            if not source.exists:
                return True
            if target.older_than(source):
                return True
        logger.debug("No changes found in %s" % resource)
        return False

    def generate_all(self, incremental=False):
        """
        Generates the entire website
        """
        logger.info("Reading site contents")
        self.load_template_if_needed()
        self.template.clear_caches()
        self.initialize()
        self.load_site_if_needed()
        self.events.begin_site()
        logger.info("Generating site to [%s]" %
                        self.site.config.deploy_root_path)
        self.__generate_node__(self.site.content, incremental)
        self.events.site_complete()
        self.finalize()
        self.generated_once = True

    def generate_node_at_path(self, node_path=None, incremental=False):
        """
        Generates a single node. If node_path is non-existent or empty,
        generates the entire site.
        """
        if not self.generated_once and not incremental:
            return self.generate_all()
        self.load_template_if_needed()
        self.load_site_if_needed()
        node = None
        if node_path:
            node = self.site.content.node_from_path(node_path)
        self.generate_node(node, incremental)

    @contextmanager
    def events_for(self, obj):
        if not self.generated_once:
            self.events.begin_site()
            if isinstance(obj, Resource):
                self.events.begin_node(obj.node)
        yield
        if not self.generated_once:
            if isinstance(obj, Resource):
                self.events.node_complete(obj.node)
            self.events.site_complete()
            self.generated_once = True

    def generate_node(self, node=None, incremental=False):
        """
        Generates the given node. If node is invalid, empty or
        non-existent, generates the entire website.
        """
        if not node or not self.generated_once and not incremental:
            return self.generate_all()

        self.load_template_if_needed()
        self.initialize()
        self.load_site_if_needed()

        try:
            with self.events_for(node):
                self.__generate_node__(node, incremental)
            self.finalize()
        except HydeException:
            self.generate_all()

    def generate_resource_at_path(self,
                    resource_path=None,
                    incremental=False):
        """
        Generates a single resource. If resource_path is non-existent or empty,
        generats the entire website.
        """
        if not self.generated_once and not incremental:
            return self.generate_all()

        self.load_template_if_needed()
        self.load_site_if_needed()
        resource = None
        if resource_path:
            resource = self.site.content.resource_from_path(resource_path)
        self.generate_resource(resource, incremental)

    def generate_resource(self, resource=None, incremental=False):
        """
        Generates the given resource. If resource is invalid, empty or
        non-existent, generates the entire website.
        """
        if not resource or not self.generated_once and not incremental:
            return self.generate_all()

        self.load_template_if_needed()
        self.initialize()
        self.load_site_if_needed()

        try:
            with self.events_for(resource):
                self.__generate_resource__(resource, incremental)
        except HydeException:
            self.generate_all()

    def refresh_config(self):
        if self.site.config.needs_refresh():
            logger.debug("Refreshing configuration and context")
            self.site.refresh_config()
            self.create_context()

    def __generate_node__(self, node, incremental=False):
        self.refresh_config()
        for node in node.walk():
            logger.debug("Generating Node [%s]", node)
            self.events.begin_node(node)
            for resource in node.resources:
                self.__generate_resource__(resource, incremental)
            self.events.node_complete(node)


    def __generate_resource__(self, resource, incremental=False):
        self.refresh_config()
        if not resource.is_processable:
            logger.debug("Skipping [%s]", resource)
            return
        if incremental and not self.has_resource_changed(resource):
            logger.debug("No changes found. Skipping resource [%s]", resource)
            return
        logger.debug("Processing [%s]", resource)
        with self.context_for_resource(resource) as context:
            target = File(self.site.config.deploy_root_path.child(
                                    resource.relative_deploy_path))
            target.parent.make()
            if resource.simple_copy:
                logger.debug("Simply Copying [%s]", resource)
                resource.source_file.copy_to(target)
            elif resource.source_file.is_text:
                self.update_deps(resource)
                if resource.uses_template:
                    logger.debug("Rendering [%s]", resource)
                    try:
                        text = self.template.render_resource(resource,
                                        context)
                    except Exception, e:
                        HydeException.reraise("Error occurred when"
                            " processing template: [%s]: %s" %
                            (resource, repr(e)),
                            sys.exc_info()
                        )
                else:
                    text = resource.source_file.read_all()
                    text = self.events.begin_text_resource(resource, text) or text

                text = self.events.text_resource_complete(
                                        resource, text) or text
                target.write(text)
                copymode(resource.source_file.path, target.path)
            else:
                logger.debug("Copying binary file [%s]", resource)
                self.events.begin_binary_resource(resource)
                resource.source_file.copy_to(target)
                self.events.binary_resource_complete(resource)
