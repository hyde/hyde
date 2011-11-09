# -*- coding: utf-8 -*-
"""
Parses & holds information about the site to be generated.
"""
import os
import fnmatch
import sys
import urlparse
from functools import wraps
from urllib import quote

from hyde.exceptions import HydeException
from hyde.fs import FS, File, Folder
from hyde.model import Config
from hyde.util import getLoggerWithNullHandler


def path_normalized(f):
    @wraps(f)
    def wrapper(self, path):
        return f(self, unicode(path).replace('/', os.sep))
    return wrapper

logger = getLoggerWithNullHandler('hyde.engine')

class Processable(object):
    """
    A node or resource.
    """

    def __init__(self, source):
        super(Processable, self).__init__()
        self.source = FS.file_or_folder(source)
        self.is_processable = True
        self.uses_template = True

    @property
    def name(self):
        """
        The resource name
        """
        return self.source.name

    def __repr__(self):
        return self.path

    @property
    def path(self):
        """
        Gets the source path of this node.
        """
        return self.source.path


class Resource(Processable):
    """
    Represents any file that is processed by hyde
    """

    def __init__(self, source_file, node):
        super(Resource, self).__init__(source_file)
        self.source_file = source_file
        if not node:
            raise HydeException("Resource cannot exist without a node")
        if not source_file:
            raise HydeException("Source file is required"
                                " to instantiate a resource")
        self.node = node
        self.site = node.site
        self._relative_deploy_path = None

    @property
    def relative_path(self):
        """
        Gets the path relative to the root folder (Content)
        """
        return self.source_file.get_relative_path(self.node.root.source_folder)

    @property
    def slug(self):
        #TODO: Add a more sophisticated slugify method
        return self.source.name_without_extension

    def get_relative_deploy_path(self):
        """
        Gets the path where the file will be created
        after its been processed.
        """
        return self._relative_deploy_path \
                    if self._relative_deploy_path \
                    else self.relative_path

    def set_relative_deploy_path(self, path):
        """
        Sets the path where the file ought to be created
        after its been processed.
        """
        self._relative_deploy_path = path
        self.site.content.resource_deploy_path_changed(self)

    relative_deploy_path = property(get_relative_deploy_path, set_relative_deploy_path)
    url = relative_deploy_path

    @property
    def full_url(self):
        """
        Returns the full url for the resource.
        """
        return self.site.full_url(self.relative_path)

class Node(Processable):
    """
    Represents any folder that is processed by hyde
    """

    def __init__(self, source_folder, parent=None):
        super(Node, self).__init__(source_folder)
        if not source_folder:
            raise HydeException("Source folder is required"
                                " to instantiate a node.")
        self.root = self
        self.module = None
        self.site = None
        self.source_folder = Folder(unicode(source_folder))
        self.parent = parent
        if parent:
            self.root = self.parent.root
            self.module = self.parent.module if self.parent.module else self
            self.site = parent.site
        self.child_nodes = []
        self.resources = []

    def contains_resource(self, resource_name):
        """
        Returns True if the given resource name exists as a file
        in this node's source folder.
        """

        return File(self.source_folder.child(resource_name)).exists

    def get_resource(self, resource_name):
        """
        Gets the resource if the given resource name exists as a file
        in this node's source folder.
        """

        if self.contains_resource(resource_name):
            return self.root.resource_from_path(
                        self.source_folder.child(resource_name))
        return None

    def add_child_node(self, folder):
        """
        Creates a new child node and adds it to the list of child nodes.
        """

        if folder.parent != self.source_folder:
            raise HydeException("The given folder [%s] is not a"
                                " direct descendant of [%s]" %
                                (folder, self.source_folder))
        node = Node(folder, self)
        self.child_nodes.append(node)
        return node

    def add_child_resource(self, afile):
        """
        Creates a new resource and adds it to the list of child resources.
        """

        if afile.parent != self.source_folder:
            raise HydeException("The given file [%s] is not"
                                " a direct descendant of [%s]" %
                                (afile, self.source_folder))
        resource = Resource(afile, self)
        self.resources.append(resource)
        return resource

    def walk(self):
        """
        Walks the node, first yielding itself then
        yielding the child nodes depth-first.
        """
        yield self
        for child in self.child_nodes:
            for node in child.walk():
                yield node

    def walk_resources(self):
        """
        Walks the resources in this hierarchy.
        """
        for node in self.walk():
            for resource in node.resources:
                yield resource

    @property
    def relative_path(self):
        """
        Gets the path relative to the root folder (Content, Media, Layout)
        """
        return self.source_folder.get_relative_path(self.root.source_folder)

    @property
    def url(self):
        return '/' + self.relative_path

    @property
    def full_url(self):
        return self.site.full_url(self.relative_path)

class RootNode(Node):
    """
    Represents one of the roots of site: Content, Media or Layout
    """

    def __init__(self, source_folder, site):
        super(RootNode, self).__init__(source_folder)
        self.site = site
        self.node_map = {}
        self.node_deploy_map = {}
        self.resource_map = {}
        self.resource_deploy_map = {}

    @path_normalized
    def node_from_path(self, path):
        """
        Gets the node that maps to the given path.
        If no match is found it returns None.
        """
        if Folder(path) == self.source_folder:
            return self
        return self.node_map.get(unicode(Folder(path)), None)

    @path_normalized
    def node_from_relative_path(self, relative_path):
        """
        Gets the content node that maps to the given relative path.
        If no match is found it returns None.
        """
        return self.node_from_path(
                    self.source_folder.child(unicode(relative_path)))

    @path_normalized
    def resource_from_path(self, path):
        """
        Gets the resource that maps to the given path.
        If no match is found it returns None.
        """
        return self.resource_map.get(unicode(File(path)), None)

    @path_normalized
    def resource_from_relative_path(self, relative_path):
        """
        Gets the content resource that maps to the given relative path.
        If no match is found it returns None.
        """
        return self.resource_from_path(
                    self.source_folder.child(relative_path))

    def resource_deploy_path_changed(self, resource):
        """
        Handles the case where the relative deploy path of a
        resource has changed.
        """
        self.resource_deploy_map[unicode(resource.relative_deploy_path)] = resource

    @path_normalized
    def resource_from_relative_deploy_path(self, relative_deploy_path):
        """
        Gets the content resource whose deploy path maps to
        the given relative path. If no match is found it returns None.
        """
        if relative_deploy_path in self.resource_deploy_map:
            return self.resource_deploy_map[relative_deploy_path]
        return self.resource_from_relative_path(relative_deploy_path)

    def add_node(self, a_folder):
        """
        Adds a new node to this folder's hierarchy.
        Also adds to to the hashtable of path to node associations
        for quick lookup.
        """
        folder = Folder(a_folder)
        node = self.node_from_path(folder)
        if node:
            logger.debug("Node exists at [%s]" % node.relative_path)
            return node

        if not folder.is_descendant_of(self.source_folder):
            raise HydeException("The given folder [%s] does not"
                                " belong to this hierarchy [%s]" %
                                (folder, self.source_folder))

        p_folder = folder
        parent = None
        hierarchy = []
        while not parent:
            hierarchy.append(p_folder)
            p_folder = p_folder.parent
            parent = self.node_from_path(p_folder)

        hierarchy.reverse()
        node = parent if parent else self
        for h_folder in hierarchy:
            node = node.add_child_node(h_folder)
            self.node_map[unicode(h_folder)] = node
            logger.debug("Added node [%s] to [%s]" % (
                            node.relative_path, self.source_folder))

        return node

    def add_resource(self, a_file):
        """
        Adds a file to the parent node.  Also adds to to the
        hashtable of path to resource associations for quick lookup.
        """

        afile = File(a_file)

        resource = self.resource_from_path(afile)
        if resource:
            logger.debug("Resource exists at [%s]" % resource.relative_path)
            return resource

        if not afile.is_descendant_of(self.source_folder):
            raise HydeException("The given file [%s] does not reside"
                                " in this hierarchy [%s]" %
                                (afile, self.source_folder))

        node = self.node_from_path(afile.parent)

        if not node:
            node = self.add_node(afile.parent)

        resource = node.add_child_resource(afile)
        self.resource_map[unicode(afile)] = resource
        logger.debug("Added resource [%s] to [%s]" %
                    (resource.relative_path, self.source_folder))
        return resource

    def load(self):
        """
        Walks the `source_folder` and loads the sitemap.
        Creates nodes and resources, reads metadata and injects attributes.
        This is the model for hyde.
        """

        if not self.source_folder.exists:
            raise HydeException("The given source folder [%s]"
                                " does not exist" % self.source_folder)

        with self.source_folder.walker as walker:

            def dont_ignore(name):
                for pattern in self.site.config.ignore:
                    if fnmatch.fnmatch(name, pattern):
                        return False
                return True

            @walker.folder_visitor
            def visit_folder(folder):
                if dont_ignore(folder.name):
                    self.add_node(folder)
                else:
                    logger.debug("Ignoring node: %s" % folder.name)
                    return False

            @walker.file_visitor
            def visit_file(afile):
                if dont_ignore(afile.name):
                    self.add_resource(afile)

class Site(object):
    """
    Represents the site to be generated.
    """

    def __init__(self, sitepath=None, config=None):
        super(Site, self).__init__()
        self.sitepath = Folder(Folder(sitepath).fully_expanded_path)
        # Add sitepath to the list of module search paths so that
        # local plugins can be included.
        sys.path.insert(0, self.sitepath.fully_expanded_path)

        self.config = config if config else Config(self.sitepath)
        self.content = RootNode(self.config.content_root_path, self)
        self.plugins = []
        self.context = {}

    def refresh_config(self):
        """
        Refreshes config data if one or more config files have
        changed. Note that this does not refresh the meta data.
        """
        if self.config.needs_refresh():
            logger.debug("Refreshing config data")
            self.config = Config(self.sitepath,
                        self.config.config_file,
                        self.config.config_dict)

    def reload_if_needed(self):
        """
        Reloads if the site has not been loaded before or if the
        configuration has changed since the last load.
        """
        if not len(self.content.child_nodes):
            self.load()

    def load(self):
        """
        Walks the content and media folders to load up the sitemap.
        """
        self.content.load()

    def content_url(self, path):
        """
        Returns the content url by appending the base url from the config
        with the given path.
        """
        return quote(Folder(self.config.base_url).child(path).replace(os.sep, '/').encode("utf-8"))

    def media_url(self, path):
        """
        Returns the media url by appending the media base url from the config
        with the given path.
        """
        return quote(Folder(self.config.media_url).child(path).replace(os.sep, '/').encode("utf-8"))

    def full_url(self, path):
        """
        Determines if the given path is media or content based on the
        configuration and returns the appropriate url.
        """
        if urlparse.urlparse(path)[:2] != ("",""):
            return path
        if self.is_media(path):
            relative_path = File(path).get_relative_path(
                                Folder(self.config.media_root))
            return self.media_url(relative_path)
        else:
            return self.content_url(path)

    def is_media(self, path):
        """
        Given the relative path, determines if it is content or media.
        """
        folder = self.content.source.child_folder(path)
        return folder.is_descendant_of(self.config.media_root_path)
