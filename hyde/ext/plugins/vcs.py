# -*- coding: utf-8 -*-
"""
Contains classes and utilities to extract information from repositories
"""

from hyde.plugin import Plugin

from datetime import datetime
from dateutil.parser import parse
import os.path
import subprocess


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
                    commits = subprocess.Popen(["git", "log", "--pretty=%ai", resource.path], stdout=subprocess.PIPE).communicate()
                    commits = commits[0].split("\n")
                    if not commits:
                        self.logger.warning("No git history for [%s]" % resource)
                except subprocess.CalledProcessError:
                    self.logger.warning("Unable to get git history for [%s]" % resource)
                    commits = None

                if created == "git":
                    if commits:
                        created = parse(commits[-1].strip())
                    else:
                        created = datetime.utcfromtimestamp(os.path.getctime(resource.path))
                    created = created.replace(tzinfo=None)
                    resource.meta.created = created
                if modified == "git":
                    if commits:
                        modified = parse(commits[0].strip())
                    else:
                        modified = datetime.utcfromtimestamp(os.path.getmtime(resource.path))
                    modified = modified.replace(tzinfo=None)
                    resource.meta.modified = modified

