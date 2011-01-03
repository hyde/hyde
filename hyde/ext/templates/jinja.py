"""
Jinja template utilties
"""

from hyde.fs import File, Folder
from hyde.template import Template
from jinja2 import contextfunction, Environment, FileSystemLoader, Undefined

class SilentUndefined(Undefined):
    def __getattr__(self, name):
        return self

    __getitem__ = __getattr__

    def __call__(self, *args, **kwargs):
        return self


@contextfunction
def media_url(context, path):
    site = context['site']
    return Folder(site.config.media_url).child(path)


@contextfunction
def content_url(context, path):
    site = context['site']
    return Folder(site.config.base_url).child(path)


# pylint: disable-msg=W0104,E0602,W0613,R0201
class Jinja2Template(Template):
    """
    The Jinja2 Template implementation
    """

    def __init__(self, sitepath):
        super(Jinja2Template, self).__init__(sitepath)

    def configure(self, config):
        """
        Uses the config object to initialize the jinja environment.
        """
        if config:
            loader = FileSystemLoader([
                            str(config.content_root_path),
                            str(config.layout_root_path),
                        ])
        else:
            loader = FileSystemLoader(str(self.sitepath))
        self.env = Environment(loader=loader, undefined=SilentUndefined)
        self.env.globals['media_url'] = media_url
        self.env.globals['content_url'] = content_url

        try:
            from typogrify.templatetags import jinja2_filters
        except ImportError:
            jinja2_filters = False

        if jinja2_filters:
            jinja2_filters.register(self.env)


    def render(self, text, context):
        """
        Renders the given resource using the context
        """
        template = self.env.from_string(text)
        return template.render(context)
