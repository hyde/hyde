"""
SSH publisher
=============
Contains classes and utilities that help publishing a hyde website
via ssh/rsync.

Usage
-----
In site.yaml, add the following lines

    publisher:
        ssh:
            type: hyde.ext.publishers.ssh.SSH
            username: username
            server: ssh.server.com
            target: /www/username/mysite/
            command: rsync
            opts: -r -e ssh

Note that the final two settings (command and opts) are optional, and the
values shown are the default. Username is also optional.
With this set, generate and publish the site as follows:

    >$ hyde gen
    >$ hyde publish -p ssh

For the above options, this will lead to execution of the following command
within the ``deploy/`` directory:

    rsync -r -e ssh ./ username@ssh.server.com:/www/username/mysite/

"""
from hyde.publisher import Publisher

from subprocess import Popen, PIPE

class SSH(Publisher):
    def initialize(self, settings):
        self.settings = settings
        self.username = settings.username
        self.server = settings.server
        self.target = settings.target
        self.command = getattr(settings, 'command', 'rsync')
        self.opts = getattr(settings, 'opts', '-r -e ssh')

    def publish(self):
        command = "{command} {opts} ./ {username}{server}:{target}".format(
            command=self.command,
            opts=self.opts,
            username=self.username+'@' if self.username else '',
            server=self.server,
            target=self.target)
        deploy_path = self.site.config.deploy_root_path.path

        cmd = Popen(command, cwd=unicode(deploy_path), stdout=PIPE, shell=True)
        cmdresult = cmd.communicate()[0]
        if cmd.returncode:
            raise Exception(cmdresult)
