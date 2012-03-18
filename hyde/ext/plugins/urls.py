# -*- coding: utf-8 -*-
"""
Contains classes and utilities related to hyde urls.
"""
import re

from hyde.fs import File, Folder
from hyde.model import Expando
from hyde.plugin import Plugin
import hyde.site
from functools import wraps
import os

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

        if (hasattr(hyde.site, '___url_cleaner_patched___')):
            return

        settings = config.urlcleaner

        def clean_url(urlgetter):
            @wraps(urlgetter)
            def wrapper(context, path, safe=None):
                url = urlgetter(context, path, safe)
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

        hyde.site.___url_cleaner_patched___ = True
        hyde.site.content_url = clean_url(hyde.site.content_url)

class SmartUrlsPlugin(Plugin):
    """
    Smart Urls plugin for hyde. Changes deployment of localized
    resources. Changes content_url, media_url functions to handle new deployment
    urls.

    For example:

    content/
      index.en.html
      index.ru.html
      index.fr.html
      photo.en.jpg
      photo.ru.jpg
      photo.jpg

    Let all index files have identical content {{content_url('photo.jpg')}},
    note that we do not use language in reference to the file. Also note that fr
    do not have localized photo.jpg.

    This will generate following deploy:

    deploy/
      photo.jpg
      en/
        index.html
        photo.jpg
      ru/
        index.html
        photo.jpg
      fr/
        index.html

    en/index.html will contain /en/photo.jpg
    ru/index.html will contain /ru/photo.jpg
    fr/index.html will contain /photo.jpg as it doesn't have localized photo

    If later you've got one for fr, all you need is to add appropriate
    photo.fr.jpg file and rebuild site. Hyde will automatically use localized
    version if it is available.
    """

    def __init__(self, site):
        super(SmartUrlsPlugin, self).__init__(site)

    def begin_site(self):
        if (hasattr(hyde.site, '___url_smarturls_patched___')):
            return

        for node in self.site.content.walk():
            for resource in node.resources:
                 try:
                     uuid = resource.meta.uuid
                     language = resource.meta.language
                 except AttributeError:
                     continue
                 resource.set_relative_deploy_path(os.path.join(language, uuid))

        def get_localized_url(urlgetter):
            @wraps(urlgetter)
            def wrapper(context, path, safe=None):
                f = File(path)
                if isinstance(context, hyde.site.Site):
                    return urlgetter(context, path, safe)
                res = context['resource']
                try:
                    localized_path = res.meta.language + os.sep + path
                except AttributeError:
                    return urlgetter(context, path, safe)
                if res.site.content.resource_from_relative_deploy_path(localized_path):
                    return urlgetter(context, localized_path, safe)
                if hasattr(self.site.config, 'urlcleaner'):
                    settings = self.site.config.urlcleaner
                    for ind in getattr(settings, 'index_file_names', ['index.html']):
                        if res.site.content.resource_from_relative_deploy_path(localized_path + '/' + ind):
                            return urlgetter(context, localized_path + '.' + ind, safe)
                    if hasattr(settings, 'strip_extensions'):
                        for ext in settings.strip_extensions:
                            if res.site.content.resource_from_relative_deploy_path(localized_path + '.' + ext):
                                return urlgetter(context, localized_path + '.' + ext, safe)
                return urlgetter(context, path, safe)
            return wrapper

        hyde.site.___url_smarturls_patched___ = True
        hyde.site.content_url = get_localized_url(hyde.site.content_url)
        hyde.site.media_url = get_localized_url(hyde.site.media_url)
