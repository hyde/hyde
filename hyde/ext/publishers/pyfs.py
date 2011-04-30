"""
Contains classes and utilities that help publishing a hyde website to
a filesystem using PyFilesystem FS objects.
"""

import getpass

from hyde.fs import File, Folder
from hyde.publisher import Publisher

from hyde.util import getLoggerWithNullHandler
logger = getLoggerWithNullHandler('hyde.ext.publishers.pyfs')


from fs.osfs import OSFS
from fs.path import pathjoin
from fs.opener import fsopendir



class PyFS(Publisher):

    def initialize(self, settings):
        self.settings = settings
        self.url = settings.url
        self.prompt_for_credentials()
        self.fs = fsopendir(self.url)

    def prompt_for_credentials(self):
        credentials = {}
        if "%(username)s" in self.url:
            print "Username: ",
            credentials["username"] = raw_input().strip()
        if "%(password)s" in self.url:
            credentials["password"] = getpass.getpass("Password: ")
        if credentials:
            self.url = self.url % credentials

    def publish(self):
        super(PyFS, self).publish()
        deploy_fs = OSFS(self.site.config.deploy_root_path.path)
        for (dirnm,filenms) in deploy_fs.walk():
            logger.info("Making directory: %s",dirnm)
            self.fs.makedir(dirnm,allow_recreate=True)
            for filenm in filenms:
                filepath = pathjoin(dirnm,filenm)
                logger.info("Uploading file: %s",filepath)
                with deploy_fs.open(filepath,"rb") as f:
                    self.fs.setcontents(filepath,f)
            for filenm in self.fs.listdir(dirnm,files_only=True):
                filepath = pathjoin(dirnm,filenm)
                if filenm not in filenms:
                    logger.info("Removing file: %s",filepath)
                    self.fs.remove(filepath)

