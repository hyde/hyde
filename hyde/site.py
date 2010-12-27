# -*- coding: utf-8 -*-
"""
Parses & holds information about the site to be generated.
"""


from hyde.fs import File, Folder
from hyde.exceptions import HydeException

import logging
import os
from logging import NullHandler
logger = logging.getLogger('hyde.site')
logger.addHandler(NullHandler())


class Resource(object):
    """
    Represents any file that is processed by hyde
    """

    def __init__(self, source_file, node):
        super(Resource, self).__init__()
        self.source_file = source_file
        if not node:
            raise HydeException("Resource cannot exist without a node")
        if not source_file:
            raise HydeException("Source file is required to instantiate a resource")
        self.node = node

    def __repr__(self):
        return self.path

    @property
    def path(self):
        """
        Gets the source path of this node.
        """
        return self.source_file.path

    @property
    def relative_path(self):
        """
        Gets the path relative to the root folder (Content, Media, Layout)
        """
        return self.source_file.get_relative_path(self.node.root.source_folder)

class Node(object):
    """
    Represents any folder that is processed by hyde
    """

    def __init__(self, source_folder, parent=None):
        super(Node, self).__init__()
        if not source_folder:
            raise HydeException("Source folder is required to instantiate a node.")
        self.root = self
        self.module = None
        self.site = None
        self.source_folder = Folder(str(source_folder))
        self.parent = parent
        if parent:
            self.root = self.parent.root
            self.module = self.parent.module if self.parent.module else self
            self.site = parent.site
        self.child_nodes = []
        self.resources = []

    def __repr__(self):
        return self.path

    def add_child_node(self, folder):
        """
        Creates a new child node and adds it to the list of child nodes.
        """

        if folder.parent != self.source_folder:
            raise HydeException("The given folder [%s] is not a direct descendant of [%s]" %
                                (folder, self.source_folder))
        node = Node(folder, self)
        self.child_nodes.append(node)
        return node

    def add_child_resource(self, afile):
        """
        Creates a new resource and adds it to the list of child resources.
        """

        if afile.parent != self.source_folder:
            raise HydeException("The given file [%s] is not a direct descendant of [%s]" %
                                (afile, self.source_folder))
        resource = Resource(afile, self)
        self.resources.append(resource)
        return resource

    @property
    def path(self):
        """
        Gets the source path of this node.
        """
        return self.source_folder.path

    @property
    def relative_path(self):
        """
        Gets the path relative to the root folder (Content, Media, Layout)
        """
        return self.source_folder.get_relative_path(self.root.source_folder)

class RootNode(Node):
    """
    Represents one of the roots of site: Content, Media or Layout
    """

    def __init__(self, source_folder, site):
         super(RootNode, self).__init__(source_folder)
         self.site = site
         self.node_map = {}
         self.resource_map = {}

    def node_from_path(self, path):
        """
        Gets the node that maps to the given path. If no match is found it returns None.
        """
        if Folder(path) == self.source_folder:
            return self
        return self.node_map.get(str(Folder(path)), None)

    def node_from_relative_path(self, relative_path):
        """
        Gets the content node that maps to the given relative path. If no match is found it returns None.
        """
        return self.node_from_path(self.source_folder.child(str(relative_path)))

    def resource_from_path(self, path):
        """
        Gets the resource that maps to the given path. If no match is found it returns None.
        """
        return self.resource_map.get(str(File(path)), None)

    def resource_from_relative_path(self, relative_path):
        """
        Gets the content resource that maps to the given relative path. If no match is found it returns None.
        """
        return self.resource_from_path(self.source_folder.child(str(relative_path)))

    def add_node(self, a_folder):
        """
        Adds a new node to this folder's hierarchy. Also adds to to the hashtable of path to
        node associations for quick lookup.
        """
        folder = Folder(a_folder)
        node = self.node_from_path(folder)
        if node:
            logger.info("Node exists at [%s]" % node.relative_path)
            return node

        if not folder.is_descendant_of(self.source_folder):
            raise HydeException("The given folder [%s] does not belong to this hierarchy [%s]" %
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
            self.node_map[str(h_folder)] = node
            logger.info("Added node [%s] to [%s]" %  (node.relative_path, self.source_folder))

        return node

    def add_resource(self, a_file):
        """
        Adds a file to the parent node.  Also adds to to the hashtable of path to
        resource associations for quick lookup.
        """

        afile = File(a_file)

        resource = self.resource_from_path(afile)
        if resource:
            logger.info("Resource exists at [%s]" % resource.relative_path)

        if not afile.is_descendant_of(self.source_folder):
            raise HydeException("The given file [%s] does not reside in this hierarchy [%s]" %
                                (afile, self.content_folder))

        node = self.node_from_path(afile.parent)

        if not node:
            node = self.add_node(afile.parent)

        resource = node.add_child_resource(afile)
        self.resource_map[str(afile)] = resource
        logger.info("Added resource [%s] to [%s]" % (resource.relative_path, self.source_folder))
        return resource

    def build(self):
        """
        Walks the `source_folder` and builds the sitemap. Creates nodes and resources,
        reads metadata and injects attributes. This is the model for hyde.
        """

        if not self.source_folder.exists:
            raise HydeException("The given source folder[%s] does not exist" % self.source_folder)

        with self.source_folder.walk() as walker:

            @walker.folder_visitor
            def visit_folder(folder):
                self.add_node(folder)

            @walker.file_visitor
            def visit_file(afile):
                self.add_resource(afile)

class Site(object):
    """
    Represents the site to be generated
    """

    def __init__(self, site_path):
        super(Site, self).__init__()
        self.site_path = Folder(str(site_path))

        # TODO: Get the value from config
        content_folder = self.site_path.child_folder('content')
        self.content = RootNode(content_folder, self)
        self.node_map = {}
        self.resource_map = {}

    def build(self):
        """
        Walks the content and media folders to build up the sitemap.
        """

        self.content.build()

