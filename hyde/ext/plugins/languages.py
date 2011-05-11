# -*- coding: utf-8 -*-
"""
Contains classes to help manage multi-language pages.
"""

from hyde.plugin import Plugin

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
        # Build association between UUID and list of resources
        for node in self.site.content.walk():
            for resource in node.resources:
                try:
                    uuid = resource.meta.uuid
                    language = resource.meta.language
                except AttributeError:
                    continue
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
