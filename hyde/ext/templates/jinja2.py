"""
Hyde Template interface realization for Jinja2
"""
from hyde.template import Template

class Jinja2Template(Template):
    def configure(self, config):
        """
        Uses the config object to initialize the jinja environment.
        """
        pass

    def render(self, template_name, context):
        pass