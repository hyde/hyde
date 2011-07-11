"""
Contains classes and utilities that help publishing a hyde website to
a filesystem using PyFilesystem FS objects.

This publisher provides an easy way to publish to FTP, SFTP, WebDAV or other
servers by specifying a PyFS filesystem URL.  For example, the following
are valid URLs that can be used with this publisher:

    ftp://my.server.com/~username/my_blog/
    dav:https://username:password@my.server.com/path/to/my/site

"""

import getpass
import hashlib

from hyde.fs import File, Folder
from hyde.publisher import Publisher

from hyde.util import getLoggerWithNullHandler
logger = getLoggerWithNullHandler('hyde.ext.publishers.pyfs')


try:
    from fs.osfs import OSFS
    from fs.path import pathjoin
    from fs.opener import fsopendir
except ImportError:
    logger.error("The PyFS publisher requires PyFilesystem v0.4 or later.")
    logger.error("`pip install -U fs` to get it.")
    raise



class PyFS(Publisher):

    def initialize(self, settings):
        self.settings = settings
        self.url = settings.url
        self.check_mtime = getattr(settings,"check_mtime",False)
        self.check_etag = getattr(settings,"check_etag",False)
        if self.check_etag and not isinstance(self.check_etag,basestring):
            raise ValueError("check_etag must name the etag algorithm")
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
        for (dirnm,local_filenms) in deploy_fs.walk():
            logger.info("Making directory: %s",dirnm)
            self.fs.makedir(dirnm,allow_recreate=True)
            remote_fileinfos = self.fs.listdirinfo(dirnm,files_only=True)
            #  Process each local file, to see if it needs updating.
            for filenm in local_filenms:
                filepath = pathjoin(dirnm,filenm)
                #  Try to find an existing remote file, to compare metadata.
                for (nm,info) in remote_fileinfos:
                    if nm == filenm:
                        break
                else:
                    info = {}
                #  Skip it if the etags match
                if self.check_etag and "etag" in info:
                    with deploy_fs.open(filepath,"rb") as f:
                        local_etag = self._calculate_etag(f)
                    if info["etag"] == local_etag:
                        logger.info("Skipping file [etag]: %s",filepath)
                        continue
                #  Skip it if the mtime is more recent remotely.
                if self.check_mtime and "modified_time" in info:
                    local_mtime = deploy_fs.getinfo(filepath)["modified_time"]
                    if info["modified_time"] > local_mtime:
                        logger.info("Skipping file [mtime]: %s",filepath)
                        continue
                #  Upload it to the remote filesystem.
                logger.info("Uploading file: %s",filepath)
                with deploy_fs.open(filepath,"rb") as f:
                    self.fs.setcontents(filepath,f)
            #  Process each remote file, to see if it needs deleting.
            for (filenm,info) in remote_fileinfos:
                filepath = pathjoin(dirnm,filenm)
                if filenm not in local_filenms:
                    logger.info("Removing file: %s",filepath)
                    self.fs.remove(filepath)

    def _calculate_etag(self,f):
        hasher = getattr(hashlib,self.check_etag.lower())()
        data = f.read(1024*64)
        while data:
            hasher.update(data)
            data = f.read(1024*64)
        return hasher.hexdigest()

