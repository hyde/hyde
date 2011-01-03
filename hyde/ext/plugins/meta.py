"""
Contains classes and utilities related to meta data in hyde.
"""
import re
from hyde.model import Expando
from hyde.plugin import Plugin
import yaml

import logging
from logging import NullHandler
logger = logging.getLogger('hyde.engine')
logger.addHandler(NullHandler())


class Metadata(Expando):
    """
    Container class for yaml meta data.
    """
    def __init__(self, text):
        super(Metadata, self).__init__(yaml.load(text))



class MetaPlugin(Plugin):
    """
    Metadata plugin for hyde. Loads meta data in the following order:

    1. meta.yaml: files in any folder
    2. frontmatter: any text file with content enclosed within three dashes.
        Example:
        ---
        abc: def
        ---

    Supports YAML syntax.
    """

    def __init__(self, site):
        super(MetaPlugin, self).__init__(site)


    def begin_text_resource(self, resource, text):
        """
        Load meta data by looking for the marker.
        Once loaded, remove the meta area from the text.
        """
        logger.info("Trying to load metadata from resource [%s]" % resource)
        # re from spjwebster's lanyon
        yaml_finder = re.compile( r"^\s*---\s*\n((?:.|\n)+?)\n---\s*\n", re.MULTILINE)
        match = re.match(yaml_finder, text)
        if not match:
            logger.info("No metadata found in resource [%s]" % resource)
            return text
        text = text[match.end():]
        resource.meta = Metadata(match.group(1))
        logger.info("Successfully loaded metadata from resource [%s]"
                        % resource)
        return text