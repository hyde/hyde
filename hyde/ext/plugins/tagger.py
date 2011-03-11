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


class TaggerPlugin(Plugin):
    """
    Tagger plugin for hyde. Adds the ability to do
    tag resources and search based on the tags.

    Configuration example
    ---------------------
    #yaml
    sorter:
        kind:
            atts: source.kind
    tagger:
       blog:
           sorter: kind # How to sort the resources in a tag
           source: blog # The source folder to look for resources
           target: blog/tags # The target folder to deploy the archives
    """
    def __init__(self, site):
        super(GrouperPlugin, self).__init__(site)

    def begin_site(self):
        """
        Initialize plugin. Add the specified groups to the
        site context variable.
        """
        config = self.site.config
        if not hasattr(config, 'grouper'):
            return
        if not hasattr(self.site, 'grouper'):
            self.site.grouper = {}

        for name, grouping in self.site.config.grouper.__dict__.items():
            grouping.name = name
            prev_att = 'prev_in_%s' % name
            next_att = 'next_in_%s' % name
            setattr(Resource, prev_att, None)
            setattr(Resource, next_att, None)
            self.site.grouper[name] = Group(grouping)
            walker = Group.walk_resources(
                            self.site.content, self.site.grouper[name])

            for prev, next in pairwalk(walker):
                setattr(next, prev_att, prev)
                setattr(prev, next_att, next)