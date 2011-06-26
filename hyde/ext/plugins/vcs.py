# -*- coding: utf-8 -*-
"""
Contains classes and utilities to extract information from repositories
"""

from hyde.plugin import Plugin

import subprocess
from dateutil.parser import parse


#
# Git Dates
#

class GitDatesPlugin(Plugin):
    """
    Extract creation and last modification date from git and include
    them in the meta data if they are set to "git". Creation date
    is put in `created` and last modification date in `modified`.
    """

    def __init__(self, site):
        super(GitDatesPlugin, self).__init__(site)

    def begin_site(self):
        """
        Initialize plugin. Retrieve dates from git
        """
        for node in self.site.content.walk():
            for resource in node.resources:
                created = None
                modified = None
                try:
                    created = resource.meta.created
                    modified = resource.meta.modified
                except AttributeError:
                    pass
                # Everything is already overrided
                if created != "git" and modified != "git":
                    continue
                # Run git log --pretty=%ai
                try:
                    commits = subprocess.check_output(["git", "log", "--pretty=%ai",
                                                       resource.path]).split("\n")
                except subprocess.CalledProcessError:
                    self.logger.warning("Unable to get git history for [%s]" % resource)
                    continue
                commits = commits[:-1]
                if not commits:
                    self.logger.warning("No git history for [%s]" % resource)
                    continue
                if created == "git":
                    created = parse(commits[-1].strip())
                    resource.meta.created = created
                if modified == "git":
                    modified = parse(commits[0].strip())
                    resource.meta.modified = modified


#
# Mercurial Dates
#

class MercurialDatesPlugin(Plugin):
    """
    Extract creation and last modification date from mercurial and
    include them in the meta data if they are set to "hg". Creation
    date is put in `created` and last modification date in `modified`.
    """

    def __init__(self, site):
        super(MercurialDatesPlugin, self).__init__(site)

    def begin_site(self):
        """
        Initialize plugin. Retrieve dates from mercurial
        """
        for node in self.site.content.walk():
            for resource in node.resources:
                created = None
                modified = None
                try:
                    created = resource.meta.created
                    modified = resource.meta.modified
                except AttributeError:
                    pass
                # Everything is already overrided
                if created != "hg" and modified != "hg":
                    continue
                # Run hg log --template={date|isodatesec}
                try:
                    commits = subprocess.check_output(["hg", "log", "--template={date|isodatesec}\n",
                                                       resource.path]).split('\n')
                except subprocess.CalledProcessError:
                    self.logger.warning("Unable to get mercurial history for [%s]" % resource)
                    continue
                commits = commits[:-1]
                if not commits:
                    self.logger.warning("No mercurial history for [%s]" % resource)
                    continue
                if created == "hg":
                    created = parse(commits[-1].strip())
                    resource.meta.created = created
                if modified == "hg":
                    modified = parse(commits[0].strip())
                    resource.meta.modified = modified

