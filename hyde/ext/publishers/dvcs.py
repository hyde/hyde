"""
Contains classes and utilities that help publishing a hyde website to
distributed version control systems.
"""

from hyde.publisher import Publisher

import abc
from subprocess import Popen, PIPE

class DVCS(Publisher):
    __metaclass__ = abc.ABCMeta

    def initialize(self, settings):
        self.settings = settings
        self.path = self.site.sitepath.child_folder(settings.path)
        self.url = settings.url
        self.branch = getattr(settings, 'branch', 'master')
        self.switch(self.branch)

    @abc.abstractmethod
    def pull(self): pass

    @abc.abstractmethod
    def push(self): pass

    @abc.abstractmethod
    def commit(self, message): pass

    @abc.abstractmethod
    def switch(self, branch): pass

    @abc.abstractmethod
    def add(self, path="."): pass

    @abc.abstractmethod
    def merge(self, branch): pass


    def publish(self):
        super(DVCS, self).publish()
        if not self.path.exists:
            raise Exception("The destination repository must exist.")
        self.site.config.deploy_root_path.copy_contents_to(self.path)
        self.add()
        self.commit(self.message)
        self.push()



class Git(DVCS):
    """
    Acts as a publisher to a git repository. Can be used to publish to
    github pages.
    """

    def add(self, path="."):
        cmd = Popen('git add "%s"' % path,
                        cwd=unicode(self.path), stdout=PIPE, shell=True)
        cmdresult = cmd.communicate()[0]
        if cmd.returncode:
            raise Exception(cmdresult)

    def pull(self):
        self.switch(self.branch)
        cmd = Popen("git pull origin %s" % self.branch,
                    cwd=unicode(self.path),
                    stdout=PIPE,
                    shell=True)
        cmdresult = cmd.communicate()[0]
        if cmd.returncode:
            raise Exception(cmdresult)

    def push(self):
        cmd = Popen("git push origin %s" % self.branch,
                    cwd=unicode(self.path), stdout=PIPE,
                    shell=True)
        cmdresult = cmd.communicate()[0]
        if cmd.returncode:
            raise Exception(cmdresult)


    def commit(self, message):
        cmd = Popen('git commit -a -m"%s"' % message,
                    cwd=unicode(self.path), stdout=PIPE, shell=True)
        cmdresult = cmd.communicate()[0]
        if cmd.returncode:
            raise Exception(cmdresult)

    def switch(self, branch):
        self.branch = branch
        cmd = Popen('git checkout %s' % branch,
                    cwd=unicode(self.path), stdout=PIPE, shell=True)
        cmdresult = cmd.communicate()[0]
        if cmd.returncode:
            raise Exception(cmdresult)

    def merge(self, branch):
        cmd = Popen('git merge %s' % branch,
                    cwd=unicode(self.path), stdout=PIPE, shell=True)
        cmdresult = cmd.communicate()[0]
        if cmd.returncode:
            raise Exception(cmdresult)