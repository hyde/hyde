"""
Contains data structures and utilities for hyde.
"""


class Expando(object):
    """
    A generic expando class that creates attributes from
    the passed in dictionary.
    """

    def __init__(self, d):
        super(Expando, self).__init__()
        self.update(d)

    def update(self, d):
        """
        Updates the expando with a new dictionary
        """
        d = d or {}
        if isinstance(d, dict):
            for key, value in d.items():
                setattr(self, key, Expando.transform(value))
        elif isinstance(d, Expando):
            self.update(d.__dict__)

    @staticmethod
    def transform(primitive):
        """
        Creates an expando object, a sequence of expando objects or just
        returns the primitive based on the primitive's type.
        """
        if isinstance(primitive, dict):
            return Expando(primitive)
        elif isinstance(primitive, (tuple, list, set, frozenset)):
            seq = type(primitive)
            return seq(Expando.transform(attr) for attr in primitive)
        else:
            return primitive

from hyde.fs import File, Folder


class Config(Expando):
    """
    Represents the hyde configuration file
    """

    def __init__(self, sitepath, config_dict=None):
        default_config = dict(
            content_root='content',
            deploy_root='deploy',
            media_root='media',
            layout_root='layout',
            media_url='/media',
            site_url='/',
            not_found='404.html',
            plugins = []
        )
        conf = dict(**default_config)
        if config_dict:
            conf.update(config_dict)
        super(Config, self).__init__(conf)
        self.sitepath = Folder(sitepath)

    @property
    def deploy_root_path(self):
        """
        Derives the deploy root path from the site path
        """
        return self.sitepath.child_folder(self.deploy_root)

    @property
    def content_root_path(self):
        """
        Derives the content root path from the site path
        """
        return self.sitepath.child_folder(self.content_root)

    @property
    def media_root_path(self):
        """
        Derives the media root path from the site path
        """
        return self.sitepath.child_folder(self.media_root)

    @property
    def layout_root_path(self):
        """
        Derives the layout root path from the site path
        """
        return self.sitepath.child_folder(self.layout_root)
