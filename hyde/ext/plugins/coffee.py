# -*- coding: utf-8 -*-
"""
Coffee plugin
"""

import traceback

from hyde.plugin import CLTransformer
from hyde.fs import File

class CoffeePlugin(CLTransformer):
    """
    The plugin class for Coffeescript
    """

    def __init__(self, site):
        super(CoffeePlugin, self).__init__(site)

    @property
    def executable_name(self):
        return "coffee"

    @property
    def plugin_name(self):
        """
        The name of the plugin.
        """
        return "Coffee"

    def begin_site(self):
        """
        Find all the coffee files and set their relative deploy path.
        """
        for resource in self.site.content.walk_resources():
            if resource.source_file.kind == 'coffee':
                new_name = resource.source_file.name_without_extension + ".js"
                target_folder = File(resource.relative_deploy_path).parent
                resource.relative_deploy_path = target_folder.child(new_name)

    def text_resource_complete(self, resource, text):
        """
        Save the file to a temporary place and run the Coffee
        compiler. Read the generated file and return the text as
        output.
        """

        if not resource.source_file.kind == 'coffee':
            return

        coffee = self.app
        source = File.make_temp(text)
        target = File.make_temp('')
        args = [unicode(coffee)]
        args.extend(["-c", "-p", unicode(source)])
        return self.call_app(args)
