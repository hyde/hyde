# -*- coding: utf-8 -*-
"""
Less css plugin
"""

from hyde.plugin import Plugin
from hyde.fs import File, Folder

import re
import subprocess
import traceback


class LessCSSPlugin(Plugin):
    """
    The plugin class for less css
    """

    def __init__(self, site):
        super(LessCSSPlugin, self).__init__(site)

    def begin_text_resource(self, resource, text):
        """
        Replace @import statements with {% include %} statements.
        """

        if not resource.source_file.kind == 'less':
            return
        import_finder = re.compile(
                            '^\\s*@import\s+(?:\'|\")([^\'\"]*)(?:\'|\")\s*\;\s*$',
                            re.MULTILINE)

        def import_to_include(match):
            if not match.lastindex:
                return ''
            path = match.groups(1)[0]
            afile = File(resource.source_file.parent.child(path))
            if len(afile.kind.strip()) == 0:
                afile = File(afile.path + '.less')
            ref = self.site.content.resource_from_path(afile.path)
            if not ref:
                raise self.template.exception_class(
                        "Cannot import from path [%s]" % afile.path)
            ref.is_processable = False
            return self.template.get_include_statement(ref.relative_path)
        text = import_finder.sub(import_to_include, text)
        return text

    def text_resource_complete(self, resource, text):
        """
        Save the file to a temporary place and run less compiler.
        Read the generated file and return the text as output.
        Set the target path to have a css extension.
        """
        if not resource.source_file.kind == 'less':
            return
        if not (hasattr(self.site.config, 'less') and
            hasattr(self.site.config.less, 'app')):
            raise self.template.exception_class(
                            "Less css path not configured. "
                            "This plugin expects `less.app` to point "
                            "to the `lessc` executable.")

        less = File(self.site.config.less.app)
        if not File(less).exists:
            raise self.template.exception_class(
                    "Cannot find the less executable. The given path [%s] "
                                "is incorrect" % less)

        source = File.make_temp(text)
        target = File.make_temp('')
        try:
            subprocess.check_call([str(less), str(source), str(target)])
        except subprocess.CalledProcessError, error:
            self.logger.error(traceback.format_exc())
            self.logger.error(error.output)
            raise self.template.exception_class(
                    "Cannot process less css. Error occurred when "
                    "processing [%s]" % resource.source_file)

        out = target.read_all()
        new_name = resource.source_file.name_without_extension + ".css"
        target_folder = File(resource.relative_path).parent
        resource.relative_deploy_path = target_folder.child(new_name)
        return out
