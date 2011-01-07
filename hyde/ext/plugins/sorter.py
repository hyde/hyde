"""
Contains classes and utilities related to sortin
resources and nodes in hyde.
"""
import re
from hyde.plugin import Plugin
from hyde.site import Node, Resource

from functools import partial
from itertools import ifilter
from operator import attrgetter

import logging
from logging import NullHandler
logger = logging.getLogger('hyde.engine')
logger.addHandler(NullHandler())


def filter_method(item, settings=None):
    """
    Returns true if all the filters in the
    given settings evaluate to True.
    """

    all_match = True
    if settings and hasattr(settings, 'filters'):
        filters = settings.filters
        for field, value in filters.__dict__.items():
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
    return sorted(resources, key=attrgetter(attr))

def make_method(method_name, method_):
    def method__(self):
        return method_(self)
    method__.__name__ = method_name
    return method__

def add_method(obj, method_name, method_, settings):
    m = make_method(method_name, partial(method_, settings=settings))
    setattr(obj, method_name, m)


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
            logger.info("Adding sort methods for [%s]" % name)
            sort_method_name = 'walk_resources_sorted_by_%s' % name
            add_method(Node, sort_method_name, sort_method, settings)
            match_method_name = 'is_%s' % name
            add_method(Resource, match_method_name, filter_method, settings)
