# -*- coding: utf-8 -*-
"""
Implements the hyde entry point commands
"""
import sys
from commando import Application, command, subcommand, param
from version import __version__


class Engine(Application):
    """
    The Hyde Application
    """

    @command(description='hyde - a python static website generator',
            epilog='Use %(prog)s {command} -h to get help on individual commands')
    @param('-v', '--version', action='version', version='%(prog)s ' + __version__)
    @param('-s', '--sitepath', action='store', default='.', help="Location of the hyde site")
    def main(self, params):
        """
        Will not be executed. A sub command is required. This function exists to provide
        common parameters for the subcommands and some generic stuff like version and
        metadata
        """
        pass

    @subcommand('init', help='Create a new hyde site')
    @param('-t', '--template', action='store', default='basic', dest='template',
            help='Overwrite the current site if it exists')
    @param('-f', '--force', action='store_true', default=False, dest='overwrite',
            help='Overwrite the current site if it exists')
    def init(self, params):
        """
        The initialize command. Creates a new site from the template at the given
        sitepath.
        """
        print params.sitepath
        print params.template
        print params.overwrite

    def start(self):
        """
        main()
        """
        args = self.parse(sys.argv[1:])
        self.run(args)


