# -*- coding: utf-8 -*-
def init(args):
    print args.sitepath
    print args.force
    print args.template
    # Ensure sitepath is okay (refer to force parameter)
    # Find template by looking at the paths
    #   1. Environment Variable
    #   2. Hyde Data Directory
    # Throw exception on failure
    # Do not delete the site path, just overwrite existing files

def gen(args): pass

def serve(args): pass

from version import __version__

# """
# Implements the hyde entry point commands
# """
# class Command(object):
#     """
#     Base class for hyde commands
#     """
#     def __init__(self, **kwargs):
#         super(Command, self).__init__(epilog='Use %(prog)s {command} -h to get help on individual commands', **kwargs)
#         self.subcommands = None
#
#     def compose(self, commands, **kwargs):
#         self.subcommands = self.add_subparsers(**kwargs)
#         for command in commands:
#             self.subcommands.add_parser(command)
#
#     def run(self, args=None):
#         """
#         Executes the command
#         """
#         options = {}
#         options.update(self.defaults)
#         if args:
#             options.update(args)
#         self.execute(options)
#
#     def execute(self):
#         """
#         Abstract method for the derived classes
#         """
#         abstract
#
# class HydeCommand(Command):
#     """
#     The parent command object.
#     """
#     def __init__(self, **kwargs):
#         super(HydeCommand, self).__init__(**kwargs)
#         self.add_argument('--version', action='version', version='%(prog)s ' + __version__)
#         self.add_argument('-s', '--sitepath', action='store', default='.', help="Location of the hyde site")
#
#
# class Initializer(Command):
#     """
#     Represents the `hyde init` command
#     """
#     def __init__(self, parent, **kwargs):
#         super(Initializer, self).__init__(**kwargs)
#         init_command.add_argument('-t', '--template', action='store', default='basic', dest='template',
#                             help='Overwrite the current site if it exists')
#         init_command.add_argument('-f', '--force', action='store_true', default=False, dest='force',
#                             help='Overwrite the current site if it exists')
#
#     def run(self):
#         """
#
#         """
#         pass