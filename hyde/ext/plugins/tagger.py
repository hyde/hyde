# -*- coding: utf-8 -*-
"""
Contains classes and utilities related to tagging
resources in hyde.
"""
import re
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
           template: tagged_posts.j2
           target: tags
           archive_extension: html
    """
    def __init__(self, site):
        super(TaggerPlugin, self).__init__(site)

    def begin_site(self):
        """
        Initialize plugin. Add tag to the site context variable.
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