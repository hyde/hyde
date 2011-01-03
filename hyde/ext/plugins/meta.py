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

    def __init__(self, data, parent=None):

        super(Metadata, self).__init__({})
        if parent:
            self.update(parent.__dict__)
        if data:
            self.update(data)

    def update(self, data):
        """
        Updates the metadata with new stuff
        """
        if isinstance(data, dict):
            super(Metadata, self).update(data)
        else:
            super(Metadata, self).update(yaml.load(data))


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

    def begin_site(self):
        metadata = self.site.config.meta if hasattr(self.site.config, 'meta') else {}
        self.site.meta = Metadata(metadata)

    def begin_node(self, node):
        """
        Look for nodemeta.yaml. Load and assign it to the node.
        """
        nodemeta = node.get_resource('nodemeta.yaml')
        parent_meta = node.parent.meta if node.parent else self.site.meta
        if nodemeta:
            nodemeta.is_processable = False
            metadata = nodemeta.source_file.read_all()
            if hasattr(node, 'meta') and node.meta:
                node.meta.update(metadata)
            else:
                node.meta = Metadata(metadata, parent=parent_meta)
        else:
            node.meta = Metadata({}, parent=parent_meta)

    def begin_text_resource(self, resource, text):
        """
        Load meta data by looking for the marker.
        Once loaded, remove the meta area from the text.
        """

        logger.info("Trying to load metadata from resource [%s]" % resource)
        yaml_finder = re.compile(
                        r"^\s*---\s*\n((?:.|\n)+?)\n\s*---\s*\n",
                        re.MULTILINE)
        match = re.match(yaml_finder, text)
        if not match:
            logger.info("No metadata found in resource [%s]" % resource)
            return text
        text = text[match.end():]
        data = match.group(1)
        if not hasattr(resource, 'meta') or not resource.meta:
            resource.meta = Metadata(data, resource.node.meta)
        else:
            resource.meta.update(data)
        logger.info("Successfully loaded metadata from resource [%s]"
                        % resource)
        return text
