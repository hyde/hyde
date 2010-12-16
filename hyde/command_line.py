# -*- coding: utf-8 -*-
"""
A nice declarative interface for Argument parser
"""
from argparse import ArgumentParser, Namespace
from collections import namedtuple

__all__ = [
                'command',
                'param',
                'Application'
          ]

class CommandLine(type):
    """
    Meta class that enables declarative command definitions
    """
    def __new__(cls, name, bases, attrs):
        instance = super(CommandLine, cls).__new__(cls, name, bases, attrs)
        subcommands = []
        main_command = None
        for name, member in attrs.iteritems():
            if hasattr(member, "command"):
                main_command = member
            # else if member.params:
            #     subcommands.append(member)
        parser = None
        if main_command:
            parser = ArgumentParser(*main_command.command.args, **main_command.command.kwargs)
            for param in main_command.params:
                parser.add_argument(*param.args, **param.kwargs)


            # subparsers = None
            # if subcommands.length:
            #     subparsers = parser.add_subparsers()
            #
            #     for command in subcommands:
            #
            #         for param in main_command.params:
            #             parser.add_argument(*param.args, **param.kwargs)

        instance.parser = parser
        instance.main = main_command
        return instance

values = namedtuple('__meta_values', 'args, kwargs')
class metarator(object):
    """
    A generic decorator that tags the decorated method with
    the passed in arguments for meta classes to process them.
    """
    def __init__(self, *args, **kwargs):
        self.values = values._make((args, kwargs))

    def metarate(self, f, name='values'):
        setattr(f, name, self.values)
        return f

    def __call__(self, f):
        return self.metarate(f)


class command(metarator):
    """
    Used to decorate the main entry point
    """
    def __call__(self, f):
        return self.metarate(f, name='command')

class param(metarator):
    """
    Use this decorator instead of `ArgumentParser.add_argument`.
    """
    def __call__(self, f):
        f.params = f.params if hasattr(f, 'params') else []
        f.params.append(self.values)
        return f


class Application(object):
    """
    Bare bones base class for command line applications. Hides the
    meta programming complexities.
    """
    __metaclass__ = CommandLine

    def parse(self, argv):
        return self.parser.parse_args(argv)

    def run(self, args):
        if hasattr(args, 'run'):
            args.run(args)
        else:
            self.main(args)