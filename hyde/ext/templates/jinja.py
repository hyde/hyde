"""
Jinja template utilties
"""
from hyde.template import Template
from jinja2 import Environment, FileSystemLoader

# pylint: disable-msg=W0104,E0602,W0613,R0201
class Jinja2Template(Template):
    """
    The Jinja2 Template implementation
    """
   
    def __init__(self, sitepath):
        super(Jinja2Template, self).__init__(sitepath)
        self.env = Environment(loader=FileSystemLoader(sitepath))

    def configure(self, config):
        """
        Uses the config object to initialize the jinja environment.
        """
        pass

    def render(self, template_name, context):
        """
        Renders the given template using the context
        """
        template = self.env.get_template(template_name)
        return template.render(context)
