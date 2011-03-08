# -*- coding: utf-8 -*-
"""
Depends plugin

/// Experimental: Not working yet.
"""

from hyde.plugin import Plugin
import re

class DependsPlugin(Plugin):
    """
    The plugin class setting explicit dependencies.
    """

    def __init__(self, site):
        super(DependsPlugin, self).__init__(site)

    def begin_text_resource(self, resource, text):
        """
        If the meta data for the resource contains a depends attribute,
        this plugin adds an entry to the depends property of the
        resource.

        The dependency can contain the following template variables:
        node, resource, site, context.

        The following strings are valid:
        '{node.module}/dependencies/{resource.source.name_without_extension}.inc'
        '{context.dependency_folder}/{resource.source.name_without_extension}.{site.meta.depext}'
        """
        depends = []
        try:
            depends = resource.meta.depends
        except AttributeError:
            pass

        if not hasattr(resource, 'depends') or not resource.depends:
            resource.depends = []

        if isinstance(depends, basestring):
            depends = [depends]

        for dep in depends:
            resource.depends.append(dep.format(node=resource.node,
                                    resource=resource,
                                    site=self.site,
                                    context=self.site.context))
        resource.depends = list(set(resource.depends))
        return text