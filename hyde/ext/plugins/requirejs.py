# -*- coding: utf-8 -*-
"""
requirejs plugin

Calls r.js optimizer in order to proces javascript files,
bundle them into one single file and compress it.

The call to r.js is being made with options -o and out. Example:

    r.js -o rjs.conf out=app.js

whereas rjs.conf is the require.js configuration file pointing
to the main javascript file as well as passing options to r.js.
The bundled and compressed result is written to 'app.js' file
within the deployment structure.

Please see the homepage of requirejs for usage details.
"""

from hyde.plugin import CLTransformer
from hyde.fs import File

import re
import subprocess

class RequireJSPlugin(CLTransformer):

    def __init__(self, site):
        super(RequireJSPlugin, self).__init__(site)

    @property
    def executable_name(self):
        return "r.js"

    def begin_site(self):
        for resource in self.site.content.walk_resources():
            if resource.source_file.name == "rjs.conf":
                new_name = "app.js"
                target_folder = File(resource.relative_deploy_path).parent
                resource.relative_deploy_path = target_folder.child(new_name)

    def text_resource_complete(self, resource, text):
        if not resource.source_file.name == 'rjs.conf':
            return

        rjs = self.app
        target = File.make_temp('')
        args = [unicode(rjs)]
        args.extend(['-o', unicode(resource), ("out=" + target.fully_expanded_path)])

        try:
            self.call_app(args)
        except subprocess.CalledProcessError:
             raise self.template.exception_class(
                    "Cannot process %s. Error occurred when "
                    "processing [%s]" % (self.app.name, resource.source_file))

        return target.read_all()
