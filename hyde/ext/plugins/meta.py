# -*- coding: utf-8 -*-
"""
Contains classes and utilities related to meta data in hyde.
"""

import re
from operator import attrgetter
from hyde.model import Expando
from hyde.plugin import Plugin
from hyde.fs import File, Folder
from hyde.site import Node
from hyde.util import add_method
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
        self.yaml_finder = re.compile(
                    r"^\s*(?:---|===)\s*\n((?:.|\n)+?)\n\s*(?:---|===)\s*\n*",
                    re.MULTILINE)

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
                if resource.source_file.is_text and not resource.simple_copy:
                    self.__read_resource__(resource, resource.source_file.read_all())

    def __read_resource__(self, resource, text):
        """
        Reads the resource metadata and assigns it to
        the resource. Load meta data by looking for the marker.
        Once loaded, remove the meta area from the text.
        """
        self.logger.debug("Trying to load metadata from resource [%s]" % resource)
        match = re.match(self.yaml_finder, text)
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


class AutoExtendPlugin(Plugin):
    """
    The plugin class for extending templates using metadata.
    """

    def __init__(self, site):
        super(AutoExtendPlugin, self).__init__(site)

    def begin_text_resource(self, resource, text):
        """
        If the meta data for the resource contains a layout attribute,
        and there is no extends statement, this plugin automatically adds
        an extends statement to the top of the file.
        """

        if not resource.uses_template:
            return text

        layout = None
        block = None
        try:
            layout = resource.meta.extends
        except AttributeError:
            pass

        try:
            block = resource.meta.default_block
        except AttributeError:
            pass

        if layout:
            self.logger.debug("Autoextending %s with %s" % (
                resource.relative_path, layout))
            extends_pattern = self.template.patterns['extends']

            if not re.search(extends_pattern, text):
                extended_text = self.template.get_extends_statement(layout)
                extended_text += '\n'
                if block:
                    extended_text += ('%s\n%s\n%s' %
                                        (self.t_block_open_tag(block),
                                            text,
                                            self.t_block_close_tag(block)))
                else:
                    extended_text += text
                return extended_text
        return text


class Tag(Expando):
    """
    A simple object that represents a tag.
    """

    def __init__(self, name):
        """
        Initialize the tag with a name.
        """
        self.name = name
        self.resources = []

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


def get_tagger_sort_method(site):
    config = site.config
    content = site.content
    walker = 'walk_resources'
    sorter = None
    try:
        sorter = attrgetter('tagger.sorter')(config)
        walker = walker + '_sorted_by_%s' % sorter
    except AttributeError:
        pass

    try:
        walker = getattr(content, walker)
    except AttributeError:
        raise self.template.exception_class(
            "Cannot find the sorter: %s" % sorter)
    return walker

def walk_resources_tagged_with(node, tag):
    tags = set(unicode(tag).split('+'))
    walker = get_tagger_sort_method(node.site)
    for resource in walker():
        try:
            taglist = set(attrgetter("meta.tags")(resource))
        except AttributeError:
            continue
        if tags <= taglist:
            yield resource

class TaggerPlugin(Plugin):
    """
    Tagger plugin for hyde. Adds the ability to do tag resources and search
    based on the tags.

    Configuration example
    ---------------------
    #yaml
    sorter:
        kind:
            atts: source.kind
    tagger:
       sorter: kind # How to sort the resources in a tag
       archives:
            blog:
               template: tagged_posts.j2
               source: blog
               target: blog/tags
               archive_extension: html
    """
    def __init__(self, site):
        super(TaggerPlugin, self).__init__(site)

    def begin_site(self):
        """
        Initialize plugin. Add tag to the site context variable
        and methods for walking tagged resources.
        """
        self.logger.debug("Adding tags from metadata")
        config = self.site.config
        content = self.site.content
        tags = {}
        add_method(Node,
            'walk_resources_tagged_with', walk_resources_tagged_with)
        walker = get_tagger_sort_method(self.site)
        for resource in walker():
            self._process_tags_in_resource(resource, tags)
        self._process_tag_metadata(tags)
        self.site.tagger = Expando(dict(tags=tags))
        self._generate_archives()

    def _process_tag_metadata(self, tags):
        """
        Parses and adds metadata to the tagger object, if the tagger
        configuration contains metadata.
        """
        try:
            tag_meta = self.site.config.tagger.tags.to_dict()
        except AttributeError:
            tag_meta = {}

        for tagname, meta in tag_meta.iteritems():
            # Don't allow name and resources in meta
            if 'resources' in meta:
                del(meta['resources'])
            if 'name' in meta:
                del(meta['name'])
            if tagname in tags:
                tags[tagname].update(meta)

    def _process_tags_in_resource(self, resource, tags):
        """
        Reads the tags associated with this resource and
        adds them to the tag list if needed.
        """
        try:
            taglist = attrgetter("meta.tags")(resource)
        except AttributeError:
            return

        for tagname in taglist:
            if not tagname in tags:
                tag = Tag(tagname)
                tags[tagname] = tag
                tag.resources.append(resource)
                add_method(Node,
                    'walk_resources_tagged_with_%s' % tagname,
                    walk_resources_tagged_with,
                    tag=tag)
            else:
                tags[tagname].resources.append(resource)
            if not hasattr(resource, 'tags'):
                setattr(resource, 'tags', [])
            resource.tags.append(tags[tagname])

    def _generate_archives(self):
        """
        Generates archives if the configuration demands.
        """
        archive_config = None

        try:
            archive_config = attrgetter("tagger.archives")(self.site.config)
        except AttributeError:
            return

        self.logger.debug("Generating archives for tags")

        for name, config in archive_config.to_dict().iteritems():
            self._create_tag_archive(config)


    def _create_tag_archive(self, config):
        """
        Generates archives for each tag based on the given configuration.
        """
        if not 'template' in config:
            raise self.template.exception_class(
                "No Template specified in tagger configuration.")
        content = self.site.content.source_folder
        source = Folder(config.get('source', ''))
        target = content.child_folder(config.get('target', 'tags'))
        if not target.exists:
            target.make()

        # Write meta data for the configuration
        meta = config.get('meta', {})
        meta_text = u''
        if meta:
            import yaml
            meta_text = yaml.dump(meta, default_flow_style=False)

        extension = config.get('extension', 'html')
        template = config['template']

        archive_text = u"""
---
extends: false
%(meta)s
---

{%% set tag = site.tagger.tags['%(tag)s'] %%}
{%% set source = site.content.node_from_relative_path('%(node)s') %%}
{%% set walker = source['walk_resources_tagged_with_%(tag)s'] %%}
{%% extends "%(template)s" %%}
"""
        for tagname, tag in self.site.tagger.tags.to_dict().iteritems():
            tag_data = {
                "tag": tagname,
                "node": source.name,
                "template": template,
                "meta": meta_text
            }
            text = archive_text % tag_data
            archive_file = File(target.child("%s.%s" % (tagname, extension)))
            archive_file.delete()
            archive_file.write(text.strip())
            self.site.content.add_resource(archive_file)

