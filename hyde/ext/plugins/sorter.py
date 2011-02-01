# -*- coding: utf-8 -*-
"""
Contains classes and utilities related to sortin
resources and nodes in hyde.
"""
import re
from hyde.model import Expando
from hyde.plugin import Plugin
from hyde.site import Node, Resource

from functools import partial
from itertools import ifilter, izip, tee, product
from operator import attrgetter

def pairwalk(iterable):
    a, b = tee(iterable)
    next(b, None)
    return izip(a, b)

def filter_method(item, settings=None):
    """
    Returns true if all the filters in the
    given settings evaluate to True.
    """
    all_match = True
    default_filters = {}
    filters = {}
    if hasattr(settings, 'filters'):
        filters.update(default_filters)
        filters.update(settings.filters.__dict__)

    for field, value in filters.items():
        try:
            res = attrgetter(field)(item)
        except:
            res = None
        if res != value:
            all_match = False
            break
    return all_match

def sort_method(node, settings=None):
    """
    Sorts the resources in the given node based on the
    given settings.
    """
    attr = 'name'
    if settings and hasattr(settings, 'attr') and settings.attr:
        attr = settings.attr
    filter_ = partial(filter_method, settings=settings)
    resources = ifilter(filter_, node.walk_resources())
    reverse = False
    if settings and hasattr(settings, 'reverse'):
        reverse = settings.reverse
    if not isinstance(attr, list):
        attr = [attr]
    return sorted(resources,
                    key=attrgetter(*attr),
                    reverse=reverse)

def make_method(method_name, method_):
    def method__(self):
        return method_(self)
    method__.__name__ = method_name
    return method__

def add_method(obj, method_name, method_, settings):
    m = make_method(method_name, partial(method_, settings=settings))
    setattr(obj, method_name, m)


# class SortGroup(Expando):
#     """
#     A wrapper around sort groups. Understand hierarchical groups
#     and group metadata.
#     """
#
#     def update(self, d):
#         """
#         Updates the Sortgroup with a new grouping
#         """
#
#         d = d or {}
#         if isinstance(d, dict):
#             for key, value in d.items():
#                 if key == "groups":
#                     for group in value:
#
#                 setattr(self, key, Expando.transform(value))
#         elif isinstance(d, Expando):
#             self.update(d.__dict__)



class SorterPlugin(Plugin):
    """
    Sorter plugin for hyde. Adds the ability to do
    sophisticated sorting by expanding the site objects
    to support prebuilt sorting methods. These methods
    can be used in the templates directly.

    Configuration example
    ---------------------
    #yaml

    sorter:
        kind:
            # Sorts by this attribute name
            # Uses `attrgetter` on the resource object
            attr: source_file.kind

            # The filters to be used before sorting
            # This can be used to remove all the items
            # that do not apply. For example,
            # filtering non html content
            filters:
                source_file.kind: html
                is_processable: True
                meta.is_listable: True
    """

    def __init__(self, site):
        super(SorterPlugin, self).__init__(site)

    def begin_site(self):
        """
        Initialize plugin. Add a sort and match method
        for every configuration mentioned in site settings
        """

        config = self.site.config
        if not hasattr(config, 'sorter'):
            return

        for name, settings in config.sorter.__dict__.items():
            self._add_groups(name, settings)
            self.logger.info("Adding sort methods for [%s]" % name)
            sort_method_name = 'walk_resources_sorted_by_%s' % name
            add_method(Node, sort_method_name, sort_method, settings)
            match_method_name = 'is_%s' % name
            add_method(Resource, match_method_name, filter_method, settings)

            prev_att = 'prev_by_%s' % name
            next_att = 'next_by_%s' % name

            setattr(Resource, prev_att, None)
            setattr(Resource, next_att, None)

            walker = getattr(self.site.content,
                                sort_method_name,
                                self.site.content.walk_resources)
            for prev, next in pairwalk(walker()):
                setattr(prev, next_att, next)
                setattr(next, prev_att, prev)

    def _add_groups(self, sorter_name, settings):
        """
        Checks if the given `settings` contains a `groups` attribute.
        If it does, it loads the specified groups into the `site` object.
        """
        if not hasattr(settings, 'grouping') or \
            not hasattr(settings.grouping, 'groups') or \
            not hasattr(settings.grouping, 'name'):
            return

        grouping = Expando(settings.grouping)
        setattr(self.site, sorter_name, grouping)

        group_dict = dict([(g.name, g) for g in grouping.groups])
        for resource in self.site.content.walk_resources():
            try:
                group_value = getattr(resource.meta, grouping.name)
            except AttributeError:
                continue
            if group_value in group_dict:
                group = group_dict[group_value]

                if not hasattr(group, 'resources'):
                    group.resources = []
                print "Adding resource[%s] to group[%s]" % (resource, group.name)
                group.resources.append(resource)