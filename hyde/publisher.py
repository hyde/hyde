import abc
from operator import attrgetter

from hyde.util import getLoggerWithNullHandler
from hyde.loader import load_python_object

"""
Contains abstract classes and utilities that help publishing a website to a
server.
"""

class Publisher(object):
    """
    The abstract base class for publishers.
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, site, settings, message):
        super(Publisher, self).__init__()
        self.logger = getLoggerWithNullHandler(
                            'hyde.engine.%s' % self.__class__.__name__)
        self.site = site
        self.message = message
        self.initialize(settings)

    @abc.abstractmethod
    def initialize(self, settings): pass

    @abc.abstractmethod
    def publish(self):
        if not self.site.config.deploy_root_path.exists:
            raise Exception("Please generate the site first")

    @staticmethod
    def load_publisher(site, publisher, message):
        try:
            settings = attrgetter("publisher.%s" % publisher)(site.config)
        except AttributeError:
            logger = getLoggerWithNullHandler('hyde.engine.publisher')
            logger.error(
                "Cannot find the publisher configuration: %s" % publisher)
            raise
        if not hasattr(settings, 'type'):
            logger.error(
                "Publisher type not specified: %s" % publisher)
            raise Exception("Please specify the publisher type in config.")
        pub_class = load_python_object(settings.type, site)
        return pub_class(site, settings, message)
