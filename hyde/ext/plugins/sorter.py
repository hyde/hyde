# -*- coding: utf-8 -*-
"""
Contains classes and utilities related to sorting
resources and nodes in hyde.
"""
import re
from hyde.model import Expando
from hyde.plugin import Plugin
from hyde.site import Node, Resource
from hyde.util import add_method, pairwalk

from itertools import ifilter
from functools import partial
from operator import attrgetter

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

def attributes_checker(item, attributes=None):
    """
    Checks if the given list of attributes exist.
    """
    try:
      x = attrgetter(*attributes)(item)
      return True
    except AttributeError:
      return False

def sort_method(node, settings=None):
    """
    Sorts the resources in the given node based on the
    given settings.
    """
    attr = 'name'
    if settings and hasattr(settings, 'attr') and settings.attr:
        attr = settings.attr
    reverse = False
    if settings and hasattr(settings, 'reverse'):
        reverse = settings.reverse
    if not isinstance(attr, list):
        attr = [attr]
    filter_ = partial(filter_method, settings=settings)

    excluder_ = partial(attributes_checker, attributes=attr)

    resources = ifilter(lambda x: excluder_(x) and filter_(x),
                        node.walk_resources())
    return sorted(resources,
                    key=attrgetter(*attr),
                    reverse=reverse)


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
            sort_method_name = 'walk_resources_sorted_by_%s' % name
            self.logger.debug("Adding sort methods for [%s]" % name)
            add_method(Node, sort_method_name, sort_method, settings=settings)
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

