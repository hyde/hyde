# -*- coding: utf-8 -*-
"""
CSS plugins
"""

from hyde.plugin import CLTransformer,Plugin
from hyde.fs import File
from hyde.exceptions import HydeException

import re
import subprocess


#
# Less CSS
#

class LessCSSPlugin(CLTransformer):
    """
    The plugin class for less css
    """

    def __init__(self, site):
        super(LessCSSPlugin, self).__init__(site)
        self.import_finder = \
            re.compile('^\\s*@import\s+(?:\'|\")([^\'\"]*)(?:\'|\")\s*\;\s*$',
                       re.MULTILINE)


    @property
    def executable_name(self):
        return "lessc"

    def _should_parse_resource(self, resource):
        """
        Check user defined
        """
        return resource.source_file.kind == 'less' and \
               getattr(resource, 'meta', {}).get('parse', True)

    def _should_replace_imports(self, resource):
        return getattr(resource, 'meta', {}).get('uses_template', True)

    def begin_site(self):
        """
        Find all the less css files and set their relative deploy path.
        """
        for resource in self.site.content.walk_resources():
            if self._should_parse_resource(resource):
                new_name = resource.source_file.name_without_extension + ".css"
                target_folder = File(resource.relative_deploy_path).parent
                resource.relative_deploy_path = target_folder.child(new_name)

    def begin_text_resource(self, resource, text):
        """
        Replace @import statements with {% include %} statements.
        """

        if not self._should_parse_resource(resource) or \
           not self._should_replace_imports(resource):
            return text

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
        text = self.import_finder.sub(import_to_include, text)
        return text


    @property
    def plugin_name(self):
        """
        The name of the plugin.
        """
        return "less"

    def text_resource_complete(self, resource, text):
        """
        Save the file to a temporary place and run less compiler.
        Read the generated file and return the text as output.
        Set the target path to have a css extension.
        """
        if not self._should_parse_resource(resource):
            return

        supported = [
            "verbose",
            ("silent", "s"),
            ("compress", "x"),
            "O0",
            "O1",
            "O2",
            "include-path="
        ]

        less = self.app
        source = File.make_temp(text)
        target = File.make_temp('')
        args = [unicode(less)]
        args.extend(self.process_args(supported))
        args.extend([unicode(source), unicode(target)])
        try:
            self.call_app(args)
        except subprocess.CalledProcessError:
             raise self.template.exception_class(
                    "Cannot process %s. Error occurred when "
                    "processing [%s]" % (self.app.name, resource.source_file))
        return target.read_all()


#
# Stylus CSS
#

class StylusPlugin(CLTransformer):
    """
    The plugin class for stylus css
    """

    def __init__(self, site):
        super(StylusPlugin, self).__init__(site)
        self.import_finder = \
            re.compile('^\\s*@import\s+(?:\'|\")([^\'\"]*)(?:\'|\")\s*\;?\s*$',
                       re.MULTILINE)

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

        def import_to_include(match):
            """
            Converts a css import statement to include statemnt.
            """
            if not match.lastindex:
                return ''
            path = match.groups(1)[0]
            afile = File(File(resource.source_file.parent.child(path)).fully_expanded_path)
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

        text = self.import_finder.sub(import_to_include, text)
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
        source = File.make_temp(text.strip())
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


#
# Clever CSS
#

class CleverCSSPlugin(Plugin):
    """
    The plugin class for CleverCSS
    """

    def __init__(self, site):
        super(CleverCSSPlugin, self).__init__(site)
        try:
            import clevercss
        except ImportError, e:
            raise HydeException('Unable to import CleverCSS: ' + e.message)
        else:
            self.clevercss = clevercss

    def _should_parse_resource(self, resource):
        """
        Check user defined
        """
        return resource.source_file.kind == 'ccss' and \
               getattr(resource, 'meta', {}).get('parse', True)

    def _should_replace_imports(self, resource):
        return getattr(resource, 'meta', {}).get('uses_template', True)

    def begin_site(self):
        """
        Find all the clevercss files and set their relative deploy path.
        """
        for resource in self.site.content.walk_resources():
            if self._should_parse_resource(resource):
                new_name = resource.source_file.name_without_extension + ".css"
                target_folder = File(resource.relative_deploy_path).parent
                resource.relative_deploy_path = target_folder.child(new_name)

    def begin_text_resource(self, resource, text):
        """
        Replace @import statements with {% include %} statements.
        """

        if not self._should_parse_resource(resource) or \
           not self._should_replace_imports(resource):
            return text

        import_finder = re.compile(
                            '^\\s*@import\s+(?:\'|\")([^\'\"]*)(?:\'|\")\s*\;\s*$',
                            re.MULTILINE)

        def import_to_include(match):
            if not match.lastindex:
                return ''
            path = match.groups(1)[0]
            afile = File(resource.source_file.parent.child(path))
            if len(afile.kind.strip()) == 0:
                afile = File(afile.path + '.ccss')
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
        Run clevercss compiler on text.
        """
        if not self._should_parse_resource(resource):
            return

        return self.clevercss.convert(text, self.settings)


#
# Sassy CSS
#

class SassyCSSPlugin(Plugin):
    """
    The plugin class for SassyCSS
    """

    def __init__(self, site):
        super(SassyCSSPlugin, self).__init__(site)
        self.sass = None
        self.scss = None
        try:
            import sass
        except ImportError, e:
            self.logger.warning('Unable to import python-scss (%s), trying pyScss instead' % e.message)
            try:
                import scss
            except ImportError, e:
                raise HydeException('Unable to import pyScss: ' + e.message)
            else:
                self.scss = scss
                from hyde.util import getLoggerWithConsoleHandler
                getLoggerWithConsoleHandler('scss')
        else:
            self.sass = sass

    def _should_parse_resource(self, resource):
        """
        Check user defined
        """
        return resource.source_file.kind == 'scss' and \
               getattr(resource, 'meta', {}).get('parse', True)

    @property
    def options(self):
        """
        Returns options depending on development mode
        """
        try:
            mode = self.site.config.mode
        except AttributeError:
            mode = "production"

        debug = mode.startswith('dev')
        opts = {'compress': not debug, 'debug_info': debug}
        site_opts = self.settings.get('options')
        if site_opts:
            opts.update(site_opts)

        return opts

    def begin_site(self):
        """
        Find all the sassycss files and set their relative deploy path.
        """
        if self.scss:
            self.scss.STATIC_URL = self.site.content_url('/')
            self.scss.STATIC_ROOT = self.site.config.content_root_path.path
            self.scss.ASSETS_URL = self.site.media_url('/')
            self.scss.ASSETS_ROOT = self.site.config.deploy_root_path.child(
                                        self.site.config.media_root)

        for resource in self.site.content.walk_resources():
            if self._should_parse_resource(resource):
                new_name = resource.source_file.name_without_extension + ".css"
                target_folder = File(resource.relative_deploy_path).parent
                resource.relative_deploy_path = target_folder.child(new_name)

    def text_resource_complete(self, resource, text):
        """
        Run sassycss compiler on text.
        """
        if not self._should_parse_resource(resource):
            return

        load_paths = [resource.source_file.parent.path] + \
                     self.settings.get('load-paths', [])
        if self.sass:
            text = self.sass.compile_string(text.encode('utf8'), include_paths=':'.join(load_paths))
        elif self.scss:
            if hasattr(self.scss, 'VERSION') and self.scss.VERSION > '1.1.3':
                self.scss.LOAD_PATHS = load_paths
            else:
                self.scss.LOAD_PATHS = ','.join(load_paths)

            scss = self.scss.Scss(scss_opts=self.options)
            text = scss.compile(text)

            resource.update_deps([d for d in scss.dependencies if not d.startswith('<string')])

        return text

