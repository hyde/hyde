# -*- coding: utf-8 -*-
"""
The command line interface for hyde.
"""
import argparse
from version import __version__
from engine import init, gen, serve


def main():
    """
    The main function called by hyde executable
    """
    # parser = argparse.ArgumentParser(description='hyde - a python static website generator',
    #                                  epilog='Use %(prog)s {command} -h to get help on individual commands')
    # parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
    # parser.add_argument('-s', '--sitepath', action='store', default='.', help="Location of the hyde site")
    # subcommands = parser.add_subparsers(title="Hyde commands",
    #                                     description="Entry points for hyde")
    # init_command = subcommands.add_parser('init', help='Create a new hyde site')
    # init_command.set_defaults(run=init)
    # init_command.add_argument('-t', '--template', action='store', default='basic', dest='template',
    #                     help='Overwrite the current site if it exists')
    # init_command.add_argument('-f', '--force', action='store_true', default=False, dest='force',
    #                     help='Overwrite the current site if it exists')
    # args = parser.parse_args()
    # args.run(args)
    # 
