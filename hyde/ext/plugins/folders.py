# -*- coding: utf-8 -*-
"""
Plugins related to folders and paths
"""

from hyde.plugin import Plugin
from hyde.fs import Folder

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


