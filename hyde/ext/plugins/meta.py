# -*- coding: utf-8 -*-
"""
Contains classes and utilities related to meta data in hyde.
"""
import re
from hyde.model import Expando
from hyde.plugin import Plugin
import yaml


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
        if isinstance(data, basestring):
            super(Metadata, self).update(yaml.load(data))
        else:
            super(Metadata, self).update(data)


class MetaPlugin(Plugin):
    """
    Metadata plugin for hyde. Loads meta data in the following order:

    1. meta.yaml: files in any folder
    2. frontmatter: any text file with content enclosed within three dashes
        or three equals signs.
        Example:
        ---
        abc: def
        ---

    Supports YAML syntax.
    """

    def __init__(self, site):
        super(MetaPlugin, self).__init__(site)

    def begin_site(self):
        """
        Initialize site meta data.

        Go through all the nodes and resources to initialize
        meta data at each level.
        """
        config = self.site.config
        metadata = config.meta if hasattr(config, 'meta') else {}
        self.site.meta = Metadata(metadata)
        self.nodemeta = 'nodemeta.yaml'
        if hasattr(self.site.meta, 'nodemeta'):
            self.nodemeta = self.site.meta.nodemeta
        for node in self.site.content.walk():
            self.__read_node__(node)
            for resource in node.resources:
                if not hasattr(resource, 'meta'):
                    resource.meta = Metadata({}, node.meta)
                if resource.source_file.is_text:
                    self.__read_resource__(resource, resource.source_file.read_all())

    def __read_resource__(self, resource, text):
        """
        Reads the resource metadata and assigns it to
        the resource. Load meta data by looking for the marker.
        Once loaded, remove the meta area from the text.
        """
        self.logger.debug("Trying to load metadata from resource [%s]" % resource)
        yaml_finder = re.compile(
                    r"^\s*(?:---|===)\s*\n((?:.|\n)+?)\n\s*(?:---|===)\s*\n*",
                    re.MULTILINE)
        match = re.match(yaml_finder, text)
        if not match:
            self.logger.debug("No metadata found in resource [%s]" % resource)
            data = {}
        else:
            text = text[match.end():]
            data = match.group(1)

        if not hasattr(resource, 'meta') or not resource.meta:
            if not hasattr(resource.node, 'meta'):
                resource.node.meta = Metadata({})
            resource.meta = Metadata(data, resource.node.meta)
        else:
            resource.meta.update(data)
        self.__update_standard_attributes__(resource)
        self.logger.debug("Successfully loaded metadata from resource [%s]"
                        % resource)
        return text or ' '

    def __update_standard_attributes__(self, obj):
        """
        Updates standard attributes on the resource and
        page based on the provided meta data.
        """
        if not hasattr(obj, 'meta'):
            return
        standard_attributes = ['is_processable', 'uses_template']
        for attr in standard_attributes:
            if hasattr(obj.meta, attr):
                setattr(obj, attr, getattr(obj.meta, attr))

    def __read_node__(self, node):
        """
        Look for nodemeta.yaml (or configured name). Load and assign it
        to the node.
        """
        nodemeta = node.get_resource(self.nodemeta)
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
        self.__update_standard_attributes__(node)

    def begin_node(self, node):
        """
        Read node meta data.
        """
        self.__read_node__(node)

    def begin_text_resource(self, resource, text):
        """
        Update the meta data again, just in case it
        has changed. Return text without meta data.
        """
        return self.__read_resource__(resource, text)
