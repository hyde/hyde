# -*- coding: utf-8 -*-
"""
Contains classes and utilities to extract information from repositories
"""

from hyde.plugin import Plugin

from datetime import datetime
from dateutil.parser import parse
import os.path
import subprocess


class VCSDatesPlugin(Plugin):
    """
    Base class for getting resource timestamps from VCS.
    """
    def __init__(self, site, vcs_name='vcs'):
        super(VCSDatesPlugin, self).__init__(site)
        self.vcs_name = vcs_name

    def begin_site(self):
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
                if created != self.vcs_name and modified != self.vcs_name:
                    continue

                date_created, date_modified = self.get_dates(resource)

                if created == "git":
                    created = date_created or \
                                datetime.utcfromtimestamp(
                                    os.path.getctime(resource.path))
                    created = created.replace(tzinfo=None)
                    resource.meta.created = created

                if modified == "git":
                    modified = date_modified or resource.source.last_modified
                    modified = modified.replace(tzinfo=None)
                    resource.meta.modified = modified


    def get_dates(self):
        """
        Extract creation and last modification date from the vcs and include
        them in the meta data if they are set to "<vcs_name>". Creation date
        is put in `created` and last modification date in `modified`.
        """
        return None, None

#
# Git Dates
#
class GitDatesPlugin(VCSDatesPlugin):
    def __init__(self, site):
        super(GitDatesPlugin, self).__init__(site, 'git')

    def get_dates(self, resource):
        """
        Retrieve dates from git
        """
        # Run git log --pretty=%ai
        try:
            commits = subprocess.check_output([
                "git",
                "log",
                "--pretty=%ai",
                resource.path
            ]).split("\n")
            commits = commits[:-1]
        except subprocess.CalledProcessError:
            self.logger.warning("Unable to get git history for [%s]" % resource)
            commits = None

        if commits:
            created = parse(commits[-1].strip())
            modified = parse(commits[0].strip())
        else:
            self.logger.warning("No git history for [%s]" % resource)
            created, modified = None, None

        return created, modified

#
# Mercurial Dates
#
class MercurialDatesPlugin(VCSDatesPlugin):

    def __init__(self, site):
        super(MercurialDatesPlugin, self).__init__(site, 'hg')

    def get_dates(self, resource):
        """
        Retrieve dates from mercurial
        """
        # Run hg log --template={date|isodatesec}
        try:
            commits = subprocess.check_output([
                            "hg", "log", "--template={date|isodatesec}\n",
                                               resource.path]).split('\n')
            commits = commits[:-1]
        except subprocess.CalledProcessError:
            self.logger.warning("Unable to get mercurial history for [%s]"
                                             % resource)
            commits = None

        if not commits:
            self.logger.warning("No mercurial history for [%s]" % resource)
            return None, None

        created = parse(commits[-1].strip())
        modified = parse(commits[0].strip())
        return created, modified
