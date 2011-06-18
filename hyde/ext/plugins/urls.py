# -*- coding: utf-8 -*-
"""
Contains classes and utilities related to hyde urls.
"""
import re

from hyde.fs import File, Folder
from hyde.model import Expando
from hyde.plugin import Plugin
from hyde.site import Site, Node, Resource

from functools import wraps

class UrlCleanerPlugin(Plugin):
    """
    Url Cleaner plugin for hyde. Adds to hyde the ability to generate clean
    urls.

    Configuration example
    ---------------------
    #yaml
    urlcleaner:
        index_file_names:
            # Identifies the files that represents a directory listing.
            # These file names are automatically stripped away when
            # the content_url function is called.
            - index.html
        strip_extensions:
            # The following extensions are automatically removed when
            # generating the urls using content_url function.
            - html
        # This option will append a slash to the end of directory paths
        append_slash: true
    """

    def __init__(self, site):
        super(UrlCleanerPlugin, self).__init__(site)

    def begin_site(self):
        """
        Replace the content_url method in the site object with a custom method
        that cleans urls based on the given configuration.
        """
        config = self.site.config

        if not hasattr(config, 'urlcleaner'):
            return

        if (hasattr(Site, '___url_cleaner_patched___')):
            return

        settings = config.urlcleaner

        def clean_url(urlgetter):
            @wraps(urlgetter)
            def wrapper(site, path):
                url = urlgetter(site, path)
                index_file_names = getattr(settings,
                                        'index_file_names',
                                        ['index.html'])
                rep = File(url)
                if rep.name in index_file_names:
                    url = rep.parent.path.rstrip('/')
                    if hasattr(settings, 'append_slash') and \
                        settings.append_slash:
                        url += '/'
                elif hasattr(settings, 'strip_extensions'):
                    if rep.kind in settings.strip_extensions:
                        url = rep.parent.child(rep.name_without_extension)
                return url or '/'
            return wrapper

        Site.___url_cleaner_patched___ = True
        Site.content_url = clean_url(Site.content_url)
