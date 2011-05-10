# -*- coding: utf-8 -*-
"""
Contains classes and utilities to extract information from git repository
"""

from hyde.plugin import Plugin

import subprocess
import traceback
from dateutil.parser import parse

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
