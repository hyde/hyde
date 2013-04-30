# -*- coding: utf-8 -*-
"""
Plugins related to structure
"""

from hyde.ext.plugins.meta import Metadata
from hyde.plugin import Plugin
from hyde.site import Resource
from hyde.util import pairwalk

from fswrap import File, Folder

import os
from fnmatch import fnmatch
import operator


#
# Folder Flattening
#

class FlattenerPlugin(Plugin):
    """
    The plugin class for flattening nested folders.
    """
    def __init__(self, site):
        super(FlattenerPlugin, self).__init__(site)

    def begin_site(self):
        """
        Finds all the folders that need flattening and changes the
        relative deploy path of all resources in those folders.
        """
        items = []
        try:
            items = self.site.config.flattener.items
        except AttributeError:
            pass

        for item in items:
            node = None
            target = ''
            try:
                node = self.site.content.node_from_relative_path(item.source)
                target = Folder(item.target)
            except AttributeError:
                continue
            if node:
                for resource in node.walk_resources():
                    target_path = target.child(resource.name)
                    self.logger.debug(
                        'Flattening resource path [%s] to [%s]' %
                            (resource, target_path))
                    resource.relative_deploy_path = target_path
                for child in node.walk():
                    child.relative_deploy_path = target.path


#
# Combine
#

class CombinePlugin(Plugin):
    """
    To use this combine, the following configuration should be added
    to meta data::
         combine:
            sort: false #Optional. Defaults to true.
            root: content/media #Optional. Path must be relative to content folder - default current folder
            recurse: true #Optional. Default false.
            files:
                - ns1.*.js
                - ns2.*.js
            where: top
            remove: yes

    `files` is a list of resources (or just a resource) that should be
    combined. Globbing is performed. `where` indicate where the
    combination should be done. This could be `top` or `bottom` of the
    file. `remove` tell if we should remove resources that have been
    combined into the resource.
    """

    def __init__(self, site):
        super(CombinePlugin, self).__init__(site)

    def _combined(self, resource):
        """
        Return the list of resources to combine to build this one.
        """
        try:
            config = resource.meta.combine
        except AttributeError:
            return []    # Not a combined resource
        try:
            files = config.files
        except AttributeError:
            raise AttributeError("No resources to combine for [%s]" % resource)
        if type(files) is str:
            files = [ files ]

        # Grab resources to combine

        # select site root
        try:
            root = self.site.content.node_from_relative_path(resource.meta.combine.root)
        except AttributeError:
            root = resource.node

        # select walker
        try:
            recurse = resource.meta.combine.recurse
        except AttributeError:
            recurse = False

        walker = root.walk_resources() if recurse else root.resources

        # Must we sort?
        try:
            sort = resource.meta.combine.sort
        except AttributeError:
            sort = True

        if sort:
            resources = sorted([r for r in walker if any(fnmatch(r.name, f) for f in files)],
                                                    key=operator.attrgetter('name'))
        else:
            resources = [(f, r) for r in walker for f in files if fnmatch(r.name, f)]
            resources = [r[1] for f in files for r in resources if f in r]

        if not resources:
            self.logger.debug("No resources to combine for [%s]" % resource)
            return []

        return resources

    def begin_site(self):
        """
        Initialize the plugin and search for the combined resources
        """
        for node in self.site.content.walk():
            for resource in node.resources:
                resources = self._combined(resource)
                if not resources:
                    continue

                # Build depends
                if not hasattr(resource, 'depends'):
                    resource.depends = []
                resource.depends.extend(
                    [r.relative_path for r in resources
                     if r.relative_path not in resource.depends])

                # Remove combined resources if needed
                if hasattr(resource.meta.combine, "remove") and \
                        resource.meta.combine.remove:
                    for r in resources:
                        self.logger.debug(
                            "Resource [%s] removed because combined" % r)
                        r.is_processable = False

    def begin_text_resource(self, resource, text):
        """
        When generating a resource, add combined file if needed.
        """
        resources = self._combined(resource)
        if not resources:
            return

        where = "bottom"
        try:
            where = resource.meta.combine.where
        except AttributeError:
            pass

        if where not in [ "top", "bottom" ]:
            raise ValueError("%r should be either `top` or `bottom`" % where)

        self.logger.debug(
            "Combining %d resources for [%s]" % (len(resources),
                                                 resource))
        if where == "top":
            return "".join([r.source.read_all() for r in resources] + [text])
        else:
            return "".join([text] + [r.source.read_all() for r in resources])


#
# Pagination
#

class Page:
    def __init__(self, posts, number):
        self.posts = posts
        self.number = number

class Paginator:
    """
    Iterates resources which have pages associated with them.
    """

    file_pattern = 'page$PAGE/$FILE$EXT'

    def __init__(self, settings):
        self.sorter = getattr(settings, 'sorter', None)
        self.size = getattr(settings, 'size', 10)
        self.file_pattern = getattr(settings, 'file_pattern', self.file_pattern)

    def _relative_url(self, source_path, number, basename, ext):
        """
        Create a new URL for a new page.  The first page keeps the same name;
        the subsequent pages are named according to file_pattern.
        """
        path = File(source_path)
        if number != 1:
            filename = self.file_pattern.replace('$PAGE', str(number)) \
                                    .replace('$FILE', basename) \
                                    .replace('$EXT', ext)
            path = path.parent.child(os.path.normpath(filename))
        return path

    def _new_resource(self, base_resource, node, page_number):
        """
        Create a new resource as a copy of a base_resource, with a page of
        resources associated with it.
        """
        res = Resource(base_resource.source_file, node)
        res.node.meta = Metadata(node.meta)
        res.meta = Metadata(base_resource.meta, res.node.meta)
        path = self._relative_url(base_resource.relative_path,
                                page_number,
                                base_resource.source_file.name_without_extension,
                                base_resource.source_file.extension)
        res.set_relative_deploy_path(path)
        return res

    @staticmethod
    def _attach_page_to_resource(page, resource):
        """
        Hook up a page and a resource.
        """
        resource.page = page
        page.resource = resource

    @staticmethod
    def _add_dependencies_to_resource(dependencies, resource):
        """
        Add a bunch of resources as dependencies to another resource.
        """
        if not hasattr(resource, 'depends'):
            resource.depends = []
        resource.depends.extend([dep.relative_path for dep in dependencies
                                if dep.relative_path not in resource.depends])

    def _walk_pages_in_node(self, node):
        """
        Segregate each resource into a page.
        """
        walker = 'walk_resources'
        if self.sorter:
            walker = 'walk_resources_sorted_by_%s' % self.sorter
        walker = getattr(node, walker, getattr(node, 'walk_resources'))

        posts = list(walker())
        number = 1
        while posts:
            yield Page(posts[:self.size], number)
            posts = posts[self.size:]
            number += 1

    def walk_paged_resources(self, node, resource):
        """
        Group the resources and return the new page resources.
        """
        added_resources = []
        pages = list(self._walk_pages_in_node(node))
        if pages:
            deps = reduce(list.__add__, [page.posts for page in pages], [])

            Paginator._attach_page_to_resource(pages[0], resource)
            Paginator._add_dependencies_to_resource(deps, resource)
            for page in pages[1:]:
                # make new resource
                new_resource = self._new_resource(resource, node, page.number)
                Paginator._attach_page_to_resource(page, new_resource)
                new_resource.depends = resource.depends
                added_resources.append(new_resource)

            for prev, next in pairwalk(pages):
                next.previous = prev
                prev.next = next

        return added_resources


class PaginatorPlugin(Plugin):
    """
    Paginator plugin.

    Configuration: in a resource's metadata:

        paginator:
            sorter: time
            size: 5
            file_pattern: page$PAGE/$FILE$EXT   # optional

    then in the resource's content:

        {% for res in resource.page.posts %}
        {% refer to res.relative_path as post %}
        {{ post }}
        {% endfor %}

        {{ resource.page.previous }}
        {{ resource.page.next }}

    """
    def __init__(self, site):
        super(PaginatorPlugin, self).__init__(site)

    def begin_site(self):
        for node in self.site.content.walk():
            added_resources = []
            paged_resources = (res for res in node.resources
                                 if hasattr(res.meta, 'paginator'))
            for resource in paged_resources:
                paginator = Paginator(resource.meta.paginator)
                added_resources += paginator.walk_paged_resources(node, resource)

            node.resources += added_resources

