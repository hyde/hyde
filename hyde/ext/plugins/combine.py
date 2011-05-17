# -*- coding: utf-8 -*-
"""
Contains classes to combine files into one
"""

from fnmatch import fnmatch

from hyde.model import Expando
from hyde.plugin import Plugin

class CombinePlugin(Plugin):
    """
    To use this combine, the following configuration should be added
    to meta data::
         combine:
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
        resources = []
        for r in resource.node.resources:
            for f in files:
                if fnmatch(r.name, f):
                    resources.append(r)
                    break
        if not resources:
            self.logger.debug("No resources to combine for [%s]" % resource)
            return []

        return sorted(resources, key=lambda r: r.name)

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

    def text_resource_complete(self, resource, text):
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
