# -*- coding: utf-8 -*-
"""
Contains classes and utilities related to tagging
resources in hyde.
"""
import re
from hyde.fs import File, Folder
from hyde.model import Expando
from hyde.plugin import Plugin
from hyde.site import Node, Resource
from hyde.util import add_method, add_property, pairwalk

from collections import namedtuple
from datetime import datetime
from functools import partial
from itertools import ifilter, izip, tee, product
from operator import attrgetter


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
{%% set walker = source.walk_resources_tagged_with_%(tag)s %%}
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