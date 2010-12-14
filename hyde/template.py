# -*- coding: utf-8 -*-
"""
Interface for hyde template engines. To use a different template engine,
the following interface must be implemented.
"""
class Template(object):
    def configure(self, config):
        """
        The config object is a simple YAML object with required settings. The template
        implementations are responsible for transforming this object to match the `settings`
        required for the template engines.
        """
        abstract

    def render(template_name, context):
        """
        Given the name of a template (partial path usually), and the context, this function
        must return the rendered string.
        """
        abstract