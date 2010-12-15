"""
Hyde Template interface realization for Jinja2
"""
from hyde.template import Template
from jinja2 import Environment, FileSystemLoader

class Jinja2Template(Template):
    def configure(self, sitepath, config):
        """
        Uses the config object to initialize the jinja environment.
        """
        self.env = Environment(loader=FileSystemLoader(sitepath))
        
    def render(self, template_name, context):
        """
        Renders the given template using the context
        """
        t = self.env.get_template(template_name)
        return t.render(context)