# -*- coding: utf-8 -*-
"""
Contains classes and utilities related to grouping
resources and nodes in hyde.
"""
import re
from hyde.model import Expando
from hyde.plugin import Plugin
from hyde.site import Node, Resource
from hyde.util import add_method

from functools import partial
from itertools import ifilter, izip, tee, product
from operator import attrgetter


class Group(Expando):
    """
    A wrapper class for groups. Adds methods for
    grouping resources.
    """

    def __init__(self, grouping):
        super(Group, self).__init__(grouping)
        name = 'group'

        if hasattr(grouping, 'name'):
            name = grouping.name

        add_method(Node,
                'walk_resources_grouped_by_%s' % name,
                Group.walk_resources,
                group=self)

    def set_expando(self, key, value):
        """
        If the key is groups, creates group objects instead of
        regular expando objects.
        """
        if key == "groups":
            self.groups = [Group(group) for group in value]
        else:
            return super(Group, self).set_expando(key, value)

    @staticmethod
    def walk_resources(node, group):
        """
        The method that gets attached to the node
        object.
        """
        return group.list_resources(node)

    def walk_groups(self):
        """
        Walks the groups in the current group
        """
        for group in self.groups:
            yield group
            group.walk_groups()


    def list_resources(self, node):
        """
        Lists the resources in the given node
        sorted based on sorter configuration in this
        group.
        """
        walker = 'walk_resources'
        if hasattr(self, 'sort_with'):
            walker = 'walk_resources_sorted_by_' + self.sort_with
        walker = getattr(node, walker, getattr(node, 'walk_resources'))

        for resource in walker():
            try:
                group_value = getattr(resource.meta, self.name)
            except AttributeError:
                continue

            if group_value == self.name:
                yield resource


class GrouperPlugin(Plugin):
    """
    Grouper plugin for hyde. Adds the ability to do
    group resources and nodes in an arbitrary
    hierarchy.

    Configuration example
    ---------------------
    #yaml
    sorter:
        kind:
            atts: source.kind
    grouper:
       hyde:
           # Categorizes the nodes and resources
           # based on the groups specified here.
           # The node and resource should be tagged
           # with the categories in their metadata
           sort_with: kind # A reference to the sorter
           description: Articles about hyde
           groups:
                -
                    name: announcements
                    description: Hyde release announcements
                -
                    name: making of
                    description: Articles about hyde design decisions
                -
                    name: tips and tricks
                    description: >
                        Helpful snippets and tweaks to
                        make hyde more awesome.
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
            self.site.grouper[name] = Group(grouping)