# -*- coding: utf-8 -*-
"""
Declarative interface for argparse
"""
from argparse import ArgumentParser
from collections import namedtuple

__all__ = [
                'command',
                'subcommand',
                'param',
                'Application'
          ]

class CommandLine(type):
    """
    Meta class that enables declarative command definitions
    """
    def __new__(mcs, name, bases, attrs):
        instance = super(CommandLine, mcs).__new__(mcs, name, bases, attrs)
        subcommands = []
        main_command = None
        for name, member in attrs.iteritems():
            if hasattr(member, "command"):
                main_command = member
            elif hasattr(member, "subcommand"):
                subcommands.append(member)
        main_parser = None
        def add_arguments(parser, params):
            """
            Adds parameters to the parser
            """
            for parameter in params:
                parser.add_argument(*parameter.args, **parameter.kwargs)
        if main_command:
            main_parser = ArgumentParser(*main_command.command.args, **main_command.command.kwargs)
            add_arguments(main_parser, main_command.params)
            subparsers = None
            if len(subcommands):
                subparsers = main_parser.add_subparsers()
                for sub in subcommands:
                    parser = subparsers.add_parser(*sub.subcommand.args, **sub.subcommand.kwargs)
                    parser.set_defaults(run=sub)
                    add_arguments(parser, sub.params)

        instance.__parser__ = main_parser
        instance.__main__ = main_command
        return instance

values = namedtuple('__meta_values', 'args, kwargs')
class metarator(object):
    """
    A generic decorator that tags the decorated method with
    the passed in arguments for meta classes to process them.
    """
    def __init__(self, *args, **kwargs):
        self.values = values._make((args, kwargs))

    def metarate(self, func, name='values'):
        """
        Set the values object to the function object's namespace
        """
        setattr(func, name, self.values)
        return func

    def __call__(self, func):
        return self.metarate(func)


class command(metarator):
    """
    Used to decorate the main entry point
    """
    def __call__(self, func):
        return self.metarate(func, name='command')

class subcommand(metarator):
    """
    Used to decorate the subcommands
    """
    def __call__(self, func):
        return self.metarate(func, name='subcommand')

class param(metarator):
    """
    Use this decorator instead of `ArgumentParser.add_argument`.
    """
    def __call__(self, func):
        func.params = func.params if hasattr(func, 'params') else []
        func.params.append(self.values)
        return func


class Application(object):
    """
    Barebones base class for command line applications.
    """
    __metaclass__ = CommandLine

    def parse(self, argv):
        """
        Simple method that delegates to the ArgumentParser
        """
        return self.__parser__.parse_args(argv)

    def run(self, args):
        """
        Runs the main command or sub command based on user input
        """
        if hasattr(args, 'run'):
            args.run(self, args)
        else:
            self.__main__(args)