# -*- coding: utf-8 -*-
"""
Contains classes to help manage multi-language pages.
"""

from hyde.plugin import Plugin

from hyde.fs import File, Folder
from hyde.model import Expando
from hyde.plugin import Plugin
from hyde.ext.plugins.meta import Metadata
import hyde.site

from functools import wraps

import os

class LanguagePlugin(Plugin):
    """
    Each page should be tagged with a language using `language` meta
    data. Each page should also have an UUID stored in `uuid` meta
    data. Pages with different languages but the same UUID will be
    considered a translation of each other.

    For example, consider that you have the following content tree:
       - `en/`
       - `fr/`

    In `en/meta.yaml`, you set `language: en` and in `fr/meta.yaml`, you
    set `language: fr`. In `en/my-first-page.html`, you put something like
    this::
         -------
         uuid: page1
         -------
         My first page

     And in `fr/ma-premiere-page.html`, you put something like this::
         -------
         uuid: page1
         -------
         Ma première page

    You'll get a `translations` attribute attached to the resource
    with the list of resources that are a translation of this one.
    """

    def __init__(self, site):
        super(LanguagePlugin, self).__init__(site)
        self.languages = {} # Associate a UUID to the list of resources available

    def begin_site(self):
        """
        Initialize plugin. Build the language tree for each node
        """

        if hasattr(self.site.config, 'languages'):
            settings = self.site.config.languages
        else:
            settings = None

        # Build association between UUID and list of resources
        for node in self.site.content.walk():
            for resource in node.resources:
                try:
                    uuid = resource.meta.uuid
                    language = resource.meta.language
                except AttributeError:
                    try:
                        i = resource.source.name_without_extension.rindex('.')
                    except ValueError:
                        continue
                    language = resource.source.name_without_extension[i+1:]
                    name_without_suffix = resource.source.name_without_extension[:i] + resource.source.extension
                    if not len(language) == 2 or not language.isalpha():
                        continue
                    uuid = os.path.join(os.path.dirname(resource.get_relative_deploy_path()), name_without_suffix)
                    if hasattr(settings, 'modify_path') and settings.modify_path:
                        resource.set_relative_deploy_path(os.path.join(language, uuid))
                    # if resource was created by plugin such as tagger or
                    # thumbnail plugin it has no metadata
                    if not hasattr(resource, 'meta'):
                        resource.meta = Metadata({})
                    resource.meta.language = language
                    resource.meta.uuid = uuid
                if uuid not in self.languages:
                    self.languages[uuid] = []
                self.languages[uuid].append(resource)
        # Add back the information about other languages
        for uuid, resources in self.languages.items():
            for resource in resources:
                language = resource.meta.language
                resource.translations = \
                    [r for r in resources
                     if r.meta.language != language]
                translations = ",".join([t.meta.language for t in resource.translations])
                self.logger.debug(
                    "Adding translations for resource [%s] from %s to %s" % (resource,
                                                                             language,
                                                                             translations))

        def get_url(urlgetter):
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
                res_localized = res.site.content.resource_from_relative_deploy_path(localized_path)
                return urlgetter(context, localized_path if res_localized else path, safe)
            return wrapper

        if hasattr(settings, 'modify_path') and settings.modify_path:
            hyde.site.content_url = get_url(hyde.site.content_url)
            hyde.site.media_url = get_url(hyde.site.media_url)
