# -*- coding: utf-8 -*-
"""
Classes, functions and utilties related to hyde layouts
"""
import os

from hyde.fs import File, Folder

HYDE_DATA = "HYDE_DATA"
LAYOUTS = "layouts"


class Layout(object):
    """
    Represents a layout package
    """

    @staticmethod
    def find_layout(layout_name='basic'):
        """
        Find the layout with a given name.
        Search order:
        1. env(HYDE_DATA)
        2. <hyde script path>/layouts/
        """
        layout_folder = None
        if HYDE_DATA in os.environ:
            layout_folder = Layout._get_layout_folder(
                                os.environ[HYDE_DATA], layout_name)
        if not layout_folder:
            layout_folder = Layout._get_layout_folder(
                                File(__file__).parent, layout_name)
        return layout_folder

    @staticmethod
    def _get_layout_folder(root, layout_name='basic'):
        """
        Finds the layout folder from the given root folder.
        If it does not exist, return None
        """
        layouts_folder = Folder(unicode(root)).child_folder(LAYOUTS)
        layout_folder = layouts_folder.child_folder(layout_name)
        return layout_folder if layout_folder.exists else None
