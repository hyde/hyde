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
from functools import partial
from itertools import ifilter, izip, tee, product
from operator import attrgetter


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
    tags = set(tag.split('+'))
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
            try:
                taglist = attrgetter("meta.tags")(resource)
            except AttributeError:
                continue
            for tag in taglist:
                if not tag in tags:
                    tags[tag] = [resource]
                    add_method(Node,
                        'walk_resources_tagged_with_%s' % tag,
                        walk_resources_tagged_with,
                        tag=tag)
                else:
                    tags[tag].append(resource)

        self.site.tagger = Expando(dict(tags=tags))

    def site_complete(self):
        """
        Generate archives.
        """

        content = self.site.content
        archive_config = None

        try:
            archive_config = attrgetter("tagger.archives")(self.site.config)
        except AttributeError:
            return

        self.logger.debug("Generating archives for tags")

        for name, config in archive_config.to_dict().iteritems():

            if not 'template' in config:
                raise self.template.exception_class(
                    "No Template sepecified in tagger configuration.")
            source = content.node_from_relative_path(config.get('source', ''))
            target = self.site.config.deploy_root_path.child_folder(
                            config.get('target', 'tags'))
            extension = config.get('extension', 'html')

            if not target.exists:
                target.make()

            template = config['template']
            text = "{%% extends \"%s\" %%}" % template

            for tag, resources in self.site.tagger.tags.to_dict().iteritems():
                context = {}
                context.update(self.site.context)
                context.update(dict(
                                    site=self.site,
                                    node=source,
                                    tag=tag,
                                    walker=getattr(source,
                                        "walk_resources_tagged_with_%s" % tag)
                                ))
                archive_text = self.template.render(text, context)
                archive_file = File(target.child("%s.%s" % (tag, extension)))
                archive_file.write(archive_text)
