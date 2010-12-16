# -*- coding: utf-8 -*-
"""
Use nose
`$ pip install nose`
`$ nosetests`
"""

from hyde.command_line import Application, command, param
from util import trap_exit
from mock import Mock, patch

@trap_exit
def test_command_basic():

    number_of_calls = 0
    class TestCommandLine(Application):

        @command(description='test')
        @param('--force', action='store_true', dest='force1')
        @param('--force2', action='store', dest='force2')
        @param('--version', action='version', version='%(prog)s 1.0')
        def main(self, params):
            assert params.force1 == eval(params.force2)
            self._main()

        def _main(): pass

    with patch.object(TestCommandLine, '_main') as _main:
        c = TestCommandLine()
        args = c.parse(['--force', '--force2', 'True'])
        c.run(args)

        args = c.parse(['--force2', 'False'])
        c.run(args)

        assert _main.call_count == 2