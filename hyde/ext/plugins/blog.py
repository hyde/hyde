# -*- coding: utf-8 -*-
"""

Plugins that are useful to blogs hosted with hyde.

"""

from hyde.plugin import Plugin


class DraftsPlugin(Plugin):


    def begin_site(self):

        in_production = self.site.config.mode.startswith('prod')
        if not in_production:
            self.logger.info(
                'Generating draft posts as the site is not in production mode.')
            return

        for resource in self.site.content.walk_resources():
            if not resource.is_processable:
                continue

            try:
                is_draft = resource.meta.is_draft
            except AttributeError:
                is_draft = False

            if is_draft:
                resource.is_processable = False

            self.logger.info(
                '%s is%s draft' % (resource,
                    '' if is_draft else ' not'))