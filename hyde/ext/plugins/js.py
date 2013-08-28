# -*- coding: utf-8 -*-
"""
JavaScript plugins
"""
import subprocess
import sys

from hyde.exceptions import HydeException
from hyde.plugin import CLTransformer

from fswrap import File


#
# Uglify JavaScript
#

class UglifyPlugin(CLTransformer):
    """
    The plugin class for Uglify JS
    """

    def __init__(self, site):
        super(UglifyPlugin, self).__init__(site)

    @property
    def executable_name(self):
        return "uglifyjs"

    @property
    def plugin_name(self):
        """
        The name of the plugin.
        """
        return "uglify"

    def text_resource_complete(self, resource, text):
        """
        If the site is in development mode, just return.
        Otherwise, save the file to a temporary place
        and run the uglify app. Read the generated file
        and return the text as output.
        """

        try:
            mode = self.site.config.mode
        except AttributeError:
            mode = "production"

        if not resource.source_file.kind == 'js':
            return

        if mode.startswith('dev'):
            self.logger.debug("Skipping uglify in development mode.")
            return

        supported = [
            "source-map",
            "source-map-root",
            "source-map-url",
            "in-source-map",
            "screw-ie8",
            "expr",
            ("prefix", "p"),
            ("beautify", "b"),
            ("mangle", "m"),
            ("reserved", "r"),
            ("compress", "c"),
            ("define", "d"),
            ("enclose", "e"),
            "comments",
            "stats",
            "wrap",
            "lint",
            "verbose"
        ]

        uglify = self.app
        source = File.make_temp(text)
        target = File.make_temp('')
        args = [unicode(uglify)]
        args.extend(self.process_args(supported))
        args.extend(["-o", unicode(target), unicode(source)])
        self.call_app(args)
        out = target.read_all()
        return out

class RequireJSPlugin(CLTransformer):
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
             HydeException.reraise(
                    "Cannot process %s. Error occurred when "
                    "processing [%s]" % (self.app.name, resource.source_file),
                    sys.exc_info())

        return target.read_all()


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
        args = [unicode(coffee)]
        args.extend(["-c", "-p", unicode(source)])
        return self.call_app(args)
