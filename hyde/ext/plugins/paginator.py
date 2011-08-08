# -*- coding: utf-8 -*-
"""
Pagination plugin.  Groups a sorted set of resources into pages and supplies
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
        the subsequent pages are formatted according to file_pattern.
        """
        path = File(source_path)
        if number != 1:
            filename = self.file_pattern.replace('$PAGE', str(number)) \
                                    .replace('$FILE', basename) \
                                    .replace('$EXT', ext)
            path = path.parent.child(os.path.normpath(filename))
        return path

    def _new_resource(self, base_resource, node, page):
        """
        Create a new resource as a copy of a base_resource, with a page of
        resources associated with it.
        """
        res = Resource(base_resource.source_file, node)
        res.page = page
        page.resource = res
        path = self._relative_url(base_resource.relative_path,
                                page.number,
                                base_resource.source_file.name_without_extension,
                                base_resource.source_file.extension)
        res.set_relative_deploy_path(path)
        return res

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
        for page in pages:
            added_resources.append(self._new_resource(resource, node, page))

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
            removed_resources = []
            paged_resources = (res for res in node.resources
                                 if hasattr(res.meta, 'paginator'))
            for resource in paged_resources:
                paginator = Paginator(resource.meta.paginator)
                removed_resources.append(resource)
                added_resources += paginator.walk_paged_resources(node, resource)

            node.resources += added_resources
            for removed in removed_resources:
                node.resources.remove(removed)
