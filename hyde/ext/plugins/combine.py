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

    `files` is a list of resources (or just a resource) that should be
    combined. Globbing is performed. `where` indicate where the
    combination should be done. This could be `top` or `bottom` of the
    file.
    """

    def __init__(self, site):
        super(CombinePlugin, self).__init__(site)

    def begin_text_resource(self, resource, text):
        """
        When generating a resource, add combined file if needed.
        """
        # Grab configuration
        try:
            config = resource.meta.combine
        except AttributeError:
            return
        # Grab file list
        try:
            files = config.files
        except AttributeError:
            raise "No resources to combine for [%s]" % resource
        if type(files) is str:
            files = [ files ]
        where = "bottom"
        try:
            where = config.where
        except AttributeError:
            pass

        if where not in [ "top", "bottom" ]:
            raise ValueError("%r should be either `top` or `bottom`" % where)

        resources = []
        for r in resource.node.resources:
            for f in files:
                if fnmatch(r.name, f):
                    resources.append(r)
                    break
        if not resources:
            self.logger.debug("No resources to combine for [%s]" % resource)
            return
        self.logger.debug(
            "Combining %d resources for [%s]" % (len(resources),
                                                 resource))
        if not hasattr(resource, 'depends'):
            resource.depends = []
        resource.depends.extend([r.relative_path for r in resources
                                 if r.relative_path not in resource.depends])
        if where == "top":
            return "".join([r.source.read_all() for r in resources] + [text])
        else:
            return "".join([text] + [r.source.read_all() for r in resources])
