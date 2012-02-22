# -*- coding: utf-8 -*-
# pylint: disable-msg=W0104,E0602,W0613,R0201
"""
classes and utilities for django templates
"""
import os

import django
print django.__file__
from hyde.exceptions import HydeException
from hyde.util import getLoggerWithNullHandler
from django.conf import settings
from django.template.loader import render_to_string,get_template,add_to_builtins
from django.template import Template
from django.template.loader_tags import ExtendsNode
import hyde
from django.template.loaders.filesystem import Loader

import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

class DjangoTemplate(hyde.template.Template):
    """
       Django Template Implementation
    """

    def __init__(self, sitepath):
        super(DjangoTemplate, self).__init__(sitepath)

    def configure(self, site, engine):

        """
        configure the django environment
        """
        self.site = site
        self.engine = engine
        self.preprocessor = (engine.preprocessor
                            if hasattr(engine, 'preprocessor') else None)
        
        try:
           from django.conf import global_settings
           defaults = global_settings.__dict__
           if site.config:
              defaults.update(site.config)        
           
           if site.config:
              template_dirs = (unicode(site.config.content_root_path),unicode(site.config.layout_root_path))
           else:
              template_dirs = (unicode(self.sitepath),)
           defaults.update({'TEMPLATE_DIRS' : template_dirs})  
           settings.configure(**defaults)
           add_to_builtins('hyde.ext.templates.django_template.templatetags.hydetags')
        except Exception, err:
              print "Site settings are not defined properly"
              print err
              raise ValueError(
                       "The given site_path [%s] has invalid settings. "
                       "Give a valid path or run -init to create a new site."
               %  self.sitepath
              )
        return 

    def clear_caches(self):
        """
        Clear all caches to prepare for regeneration
        """
        from django.template.loader import template_source_loaders
        if template_source_loaders:
            for loader in template_source_loaders: 
                  loader.reset()
        return

    def get_dependencies(self, path):
        """
        Finds dependencies hierarchically based on the included
        files.
        """
        template = path.replace(os.sep, '/')
        logger.debug("Loading template [%s] and preprocessing" % template)
        loader = Loader()
        contents,file_name = loader.load_template_source(template)
        if self.preprocessor:
            resource = self.site.content.resource_from_relative_path(template)
            if resource:
                contents = self.preprocessor(resource, contents) or contents
        parsed_template  = Template(contents)
        extend_nodes = parsed_template.nodelist.get_nodes_by_type(ExtendsNode)
        tpls = [node.parent_name for node in extend_nodes]
        deps = []
        for dep in tpls:
            deps.append(dep)
            if dep:
                deps.extend(self.get_dependencies(dep))
        return list(set(deps))
 

    def render_resource(self, resource, context):
        """
        This function must load the file represented by the resource
        object and return the rendered text.
        """
        return render_to_string(resource.source_file.path,context)

    def render(self, text, context):
        """
        Given the text, and the context, this function must return the
        rendered string.
        """
        template = Template(text)
        return template.render(context)

    @property
    def exception_class(self):
        return TemplateSyntaxError

    @property
    def patterns(self):
        """
        Patterns for matching selected template statements.
        """
        return {
           "block_open": '\s*\{\%\s*block\s*([^\s]+)\s*\%\}',
           "block_close": '\s*\{\%\s*endblock\s*([^\s]*)\s*\%\}',
           "include": '\s*\{\%\s*include\s*(?:\'|\")(.+?\.[^.]*)(?:\'|\")\s*\%\}',
           "extends": '\s*\{\%\s*extends\s*(?:\'|\")(.+?\.[^.]*)(?:\'|\")\s*\%\}'
        }


    def get_include_statement(self, path_to_include):
        """
        Returns an include statement for the current template,
        given the path to include.
        """
        return '{% include "%s" %}' % path_to_include

    def get_extends_statement(self, path_to_extend):
        """
        Returns an extends statement for the current template,
        given the path to extend.
        """
        return '{% extends "%s" %}' % path_to_extend

    def get_open_tag(self, tag, params):
        """
        Returns an open tag statement.
        """
        return '{% %s %s %}' % (tag, params)

    def get_close_tag(self, tag, params):
        """
        Returns an open tag statement.
        """
        return '{% end%s %}' % tag

    def get_content_url_statement(self, url):
        """
        Returns the content url statement.
        """
        return '{% content_url "%s" %}' % url

    def get_media_url_statement(self, url):
        """
        Returns the media url statement.
        """
        return '{% media_url "%s" %}' % url

    def get_full_url_statement(self, url):
        """
        Returns the full url statement.
        """
        return '{% full_url "%s" %}' % url
