from hyde.ext.templates.jinja import HydeLoader
from hyde.plugin import Plugin

from jinja2.loaders import FileSystemLoader
from yammy.translator import yammy_to_html_string


class YammyHydeLoader(HydeLoader):
    def get_html_source(self, get_source, environment, template):
        contents, filename, uptodate = get_source(environment, template)
        contents = yammy_to_html_string(contents, keep_line_numbers=False)
        return contents, filename, uptodate

    def get_source(self, environment, template):
        source = super(YammyHydeLoader, self).get_source
        return self.get_html_source(source, environment, template)


class YammyPlugin(Plugin):
    def template_loaded(self, template):
        loader = template.env.loader
        template.env.loader = YammyHydeLoader(
                loader.searchpath,
                loader.site,
                loader.preprocessor,
                )
        super(YammyPlugin, self).template_loaded(template)
