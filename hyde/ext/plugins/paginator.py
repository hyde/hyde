# -*- coding: utf-8 -*-
"""
Paginator plugin.  Groups a sorted set of resources into pages and supplies
each page to a copy of the original resource.
"""
import os

from hyde.fs import File
from hyde.plugin import Plugin
from hyde.site import Resource
from hyde.util import pairwalk

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
        {% refer to res.url as post %}
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
