# -*- coding: utf-8 -*-
"""
requirejs plugin
"""

from hyde.plugin import CLTransformer
from hyde.fs import File

import re
import subprocess


class RequireJSPlugin(CLTransformer):
    """
    The plugin class for requirejs
    """

    def __init__(self, site):
        super(RequireJSPlugin, self).__init__(site)

    @property
    def executable_name(self):
        return "r.js"

    def _should_replace_imports(self, resource):
        return getattr(resource, 'meta', {}).get('uses_template', True)

    def begin_site(self):
        """
        Find all the less css files and set their relative deploy path.
        """
        for resource in self.site.content.walk_resources():
            if resource.source_file.name_without_extension == "main" and resource.source_file.kind == "js":
                new_name = resource.source_file.name_without_extension + "-bin.js"
                target_folder = File(resource.relative_deploy_path).parent
                resource.relative_deploy_path = target_folder.child(new_name)

    @property
    def plugin_name(self):
        """
        The name of the plugin.
        """
        return "rjs"

    def text_resource_complete(self, resource, text):
        """
        Save the file to a temporary place and run less compiler.
        Read the generated file and return the text as output.
        Set the target path to have a css extension.
        """
        if not resource.source_file.kind == 'js' and not resource.source_file.name_without_extension == "main":
            return

        rjs = self.app
        source = File.make_temp(text)
        target = File.make_temp('')
        args = [unicode(rjs)]
        args.extend(['-o'])
        args.extend([unicode(source)])
        args.extend([("out=" + target.fully_expanded_path)])
        try:
            self.call_app(args)
        except subprocess.CalledProcessError:
             raise self.template.exception_class(
                    "Cannot process %s. Error occurred when "
                    "processing [%s]" % (self.app.name, resource.source_file))
        return target.read_all()
