"""
Hyde Template interface realization for Jinja2
"""
from hyde.template import Template

class Jinja2Template(Template):
    def setup_env(config):
        """
        Uses the config object to initialize the jinja environment.
        """
        pass

    def render(template_name, context):
        pass