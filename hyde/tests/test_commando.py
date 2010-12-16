# -*- coding: utf-8 -*-
"""
Use nose
`$ pip install nose`
`$ nosetests`
"""

from contextlib import nested
from hyde.commando import Application, command, subcommand, param
from util import trap_exit_pass, trap_exit_fail
from mock import Mock, patch
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

import sys

class BasicCommandLine(Application):

    @command(description='test', prog='Basic')
    @param('--force', action='store_true', dest='force1')
    @param('--force2', action='store', dest='force2')
    @param('--version', action='version', version='%(prog)s 1.0')
    def main(self, params):
        assert params.force1 == eval(params.force2)
        self._main()

    def _main(): pass


@trap_exit_fail
def test_command_basic():

    with patch.object(BasicCommandLine, '_main') as _main:
        c = BasicCommandLine()
        args = c.parse(['--force', '--force2', 'True'])
        c.run(args)
        assert _main.call_count == 1

        args = c.parse(['--force2', 'False'])
        c.run(args)

        assert _main.call_count == 2


def test_command_version():
    with patch.object(BasicCommandLine, '_main') as _main:
        c = BasicCommandLine()
        exception = False
        try:
            c.parse(['--version'])
            assert False
        except SystemExit:
            exception = True
        assert exception
        assert not _main.called

class ComplexCommandLine(Application):

       @command(description='test', prog='Complex')
       @param('--force', action='store_true', dest='force1')
       @param('--force2', action='store', dest='force2')
       @param('--version', action='version', version='%(prog)s 1.0')
       def main(self, params):
           assert params.force1 == eval(params.force2)
           self._main()

       @subcommand('sub', description='test')
       @param('--launch', action='store_true', dest='launch1')
       @param('--launch2', action='store', dest='launch2')
       def sub(self, params):
           assert params.launch1 == eval(params.launch2)
           self._sub()

       def _main(): pass
       def _sub(): pass


@trap_exit_pass
def test_command_subcommands_usage():
    with nested(patch.object(ComplexCommandLine, '_main'),
                patch.object(ComplexCommandLine, '_sub')) as (_main, _sub):
        c = ComplexCommandLine()
        c.parse(['--usage'])

@trap_exit_fail
def test_command_subcommands():
    with nested(patch.object(ComplexCommandLine, '_main'),
                patch.object(ComplexCommandLine, '_sub')) as (_main, _sub):
        c = ComplexCommandLine()
        args = c.parse(['sub', '--launch', '--launch2', 'True'])
        c.run(args)
        assert not _main.called
        assert _sub.call_count == 1