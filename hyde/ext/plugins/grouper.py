# -*- coding: utf-8 -*-
"""
Contains classes and utilities related to grouping
resources and nodes in hyde.
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


Grouper = namedtuple('Grouper', 'group resources')

class Group(Expando):
    """
    A wrapper class for groups. Adds methods for
    grouping resources.
    """

    def __init__(self, grouping, parent=None):
        self.name = 'groups'
        self.parent = parent
        self.root = self
        self.root = parent.root if parent else self
        self.groups = []
        self.sorter = getattr(grouping, 'sorter', None)
        if hasattr(parent, 'sorter'):
            self.sorter = parent.sorter
        super(Group, self).__init__(grouping)

        add_method(Node,
                'walk_%s_groups' % self.name,
                Group.walk_groups_in_node,
                group=self)
        add_method(Node,
                'walk_resources_grouped_by_%s' % self.name,
                Group.walk_resources,
                group=self)
        add_property(Resource,
                    '%s_group' % self.name,
                    Group.get_resource_group,
                    group=self)
        add_method(Resource,
                    'walk_%s_groups' % self.name,
                    Group.walk_resource_groups,
                    group=self)

    def set_expando(self, key, value):
        """
        If the key is groups, creates group objects instead of
        regular expando objects.
        """
        if key == "groups":
            self.groups = [Group(group, parent=self) for group in value]
        else:
            return super(Group, self).set_expando(key, value)

    @staticmethod
    def get_resource_group(resource, group):
        """
        This method gets attached to the resource object.
        Returns group and its ancestors that the resource
        belongs to, in that order.
        """
        try:
            group_name = getattr(resource.meta, group.root.name)
        except AttributeError:
            group_name = None

        return next((g for g in group.walk_groups()
                            if g.name == group_name), None) \
                    if group_name \
                    else None

    @staticmethod
    def walk_resource_groups(resource, group):
        """
        This method gets attached to the resource object.
        Returns group and its ancestors that the resource
        belongs to, in that order.
        """
        try:
            group_name = getattr(resource.meta, group.root.name)
        except AttributeError:
            group_name = None
        if group_name:
            for g in group.walk_groups():
                if g.name == group_name:
                    return reversed(list(g.walk_hierarchy()))
        return []

    @staticmethod
    def walk_resources(node, group):
        """
        The method that gets attached to the node
        object for walking the resources in the node
        that belong to this group.
        """
        for group in group.walk_groups():
            for resource in group.walk_resources_in_node(node):
                yield resource

    @staticmethod
    def walk_groups_in_node(node, group):
        """
        The method that gets attached to the node
        object for walking the groups in the node.
        """
        walker = group.walk_groups()
        for g in walker:
            lister = g.walk_resources_in_node(node)
            yield Grouper(group=g, resources=lister)

    def walk_hierarchy(self):
        """
        Walks the group hierarchy starting from
        this group.
        """
        g = self
        yield g
        while g.parent:
            yield g.parent
            g = g.parent

    def walk_groups(self):
        """
        Walks the groups in the current group
        """
        yield self
        for group in self.groups:
            for child in group.walk_groups():
                yield child

    def walk_resources_in_node(self, node):
        """
        Walks the resources in the given node
        sorted based on sorter configuration in this
        group.
        """
        walker = 'walk_resources'
        if hasattr(self, 'sorter') and self.sorter:
            walker = 'walk_resources_sorted_by_' + self.sorter
        walker = getattr(node, walker, getattr(node, 'walk_resources'))
        for resource in walker():
            try:
                group_value = getattr(resource.meta, self.root.name)
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
           sorter: kind # A reference to the sorter
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