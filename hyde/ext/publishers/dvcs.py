import sys
import abc

from hyde.loader import load_python_object

class DVCS(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, path, settings):
        self.path = path
        self.url = settings.url
        self.branch = settings.branch
        self.switch(self.branch)
        self.settings = settings

    @abc.abstractmethod
    def save_draft(self, message=None): pass

    @abc.abstractmethod
    def publish(self): pass

    @abc.abstractmethod
    def pull(self): pass

    @abc.abstractmethod
    def push(self, branch): pass

    @abc.abstractmethod
    def commit(self, message): pass

    @abc.abstractmethod
    def switch(self, branch): pass

    @abc.abstractmethod
    def add_file(self, path, message=None): pass

    @abc.abstractmethod
    def merge(self, branch): pass

    @staticmethod
    def load_dvcs(path, settings):
        repo_class = load_python_object(settings['type'])
        return repo_class(path, repo)

