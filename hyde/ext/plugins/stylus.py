# -*- coding: utf-8 -*-
"""
Less css plugin
"""

from hyde.plugin import CLTransformer
from hyde.fs import File

import re
import subprocess


class StylusPlugin(CLTransformer):
    """
    The plugin class for less css
    """

    def __init__(self, site):
        super(StylusPlugin, self).__init__(site)

    def begin_site(self):
        """
        Find all the styl files and set their relative deploy path.
        """
        for resource in self.site.content.walk_resources():
            if resource.source_file.kind == 'styl':
                new_name = resource.source_file.name_without_extension + ".css"
                target_folder = File(resource.relative_deploy_path).parent
                resource.relative_deploy_path = target_folder.child(new_name)

    def begin_text_resource(self, resource, text):
        """
        Replace @import statements with {% include %} statements.
        """

        if not resource.source_file.kind == 'styl':
            return
        import_finder = re.compile(
                    '^\\s*@import\s+(?:\'|\")([^\'\"]*)(?:\'|\")\s*\;?\s*$',
                    re.MULTILINE)

        def import_to_include(match):
            """
            Converts a css import statement to include statemnt.
            """
            if not match.lastindex:
                return ''
            path = match.groups(1)[0]
            afile = File(resource.source_file.parent.child(path))
            if len(afile.kind.strip()) == 0:
                afile = File(afile.path + '.styl')
            ref = self.site.content.resource_from_path(afile.path)

            if not ref:
                try:
                    include = self.settings.args.include
                except AttributeError:
                    include = False
                if not include:
                    raise self.template.exception_class(
                        "Cannot import from path [%s]" % afile.path)
            else:
                ref.is_processable = False
                return "\n" + \
                        self.template.get_include_statement(ref.relative_path) + \
                        "\n"
            return '@import "' + path + '"\n'

        text = import_finder.sub(import_to_include, text)
        return text

    @property
    def defaults(self):
        """
        Returns `compress` if not in development mode.
        """
        try:
            mode = self.site.config.mode
        except AttributeError:
            mode = "production"

        defaults = {"compress":""}
        if mode.startswith('dev'):
            defaults = {}
        return defaults

    @property
    def plugin_name(self):
        """
        The name of the plugin.
        """
        return "stylus"

    def text_resource_complete(self, resource, text):
        """
        Save the file to a temporary place and run stylus compiler.
        Read the generated file and return the text as output.
        Set the target path to have a css extension.
        """
        if not resource.source_file.kind == 'styl':
            return
        stylus = self.app
        source = File.make_temp(text)
        target = source
        supported = [("compress", "c"), ("include", "I")]

        args = [unicode(stylus)]
        args.extend(self.process_args(supported))
        args.append(unicode(source))
        try:
            self.call_app(args)
        except subprocess.CalledProcessError, e:
            raise self.template.exception_class(
                    "Cannot process %s. Error occurred when "
                    "processing [%s]" % (stylus.name, resource.source_file))
        return target.read_all()
