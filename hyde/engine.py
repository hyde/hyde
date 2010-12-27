# -*- coding: utf-8 -*-
"""
Implements the hyde entry point commands
"""
from commando import *
from hyde.exceptions import HydeException
from hyde.fs import File, Folder
from hyde.layout import Layout, HYDE_DATA
from hyde.version import __version__

import os

HYDE_LAYOUTS = "HYDE_LAYOUTS"

class Engine(Application):
    """
    The Hyde Application
    """

    @command(description='hyde - a python static website generator',
            epilog='Use %(prog)s {command} -h to get help on individual commands')
    @version('-v', '--version', version='%(prog)s ' + __version__)
    @store('-s', '--sitepath', default='.', help="Location of the hyde site")
    def main(self, args):
        """
        Will not be executed. A sub command is required. This function exists to provide
        common parameters for the subcommands and some generic stuff like version and
        metadata
        """
        pass

    @subcommand('init', help='Create a new hyde site')
    @store('-l', '--layout', default='basic', help='Layout for the new site')
    @true('-f', '--force', default=False, dest='overwrite',
                                          help='Overwrite the current site if it exists')
    def init(self, args):
        """
        The initialize command. Creates a new site from the template at the given
        sitepath.
        """
        sitepath = File(args.sitepath)
        if sitepath.exists and not args.overwrite:
            raise HydeException("The given site path[%s] is not empty" % sitepath)
        layout = Layout.find_layout(args.layout)
        if not layout or not layout.exists:
            raise HydeException(
            "The given layout is invalid. Please check if you have the `layout` "
            "in the right place and the environment variable(%s) has been setup "
            "properly if you are using custom path for layouts" % HYDE_DATA)
        layout.copy_contents_to(args.sitepath)

    @subcommand('gen', help='Generate the site')
    @store('-c', '--config-path', default='site.yaml', help='The configuration used to generate the site')
    @store('-d', '--deploy-path', default='deploy', help='Where should the site be generated?')
    def gen(self, args):
        """
        The generate command. Generates the site at the given deployment directory.
        """
        sitepath = File(args.sitepath)
        # Read the configuration
        # Find the appropriate template environment
        # Configure the environment
        # Prepare site info
        # Generate site one file at a time