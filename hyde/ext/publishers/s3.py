"""
Contains class that helpa publishing a hyde website to Amazon S3.
Depends on boto package.
"""

from hyde.publisher import Publisher
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from hyde.fs import File, Folder
from time import strptime, mktime
from os.path import getmtime
from os import sep as path_separator

from hyde.util import getLoggerWithNullHandler
logger = getLoggerWithNullHandler('hyde.ext.publishers.s3')

class S3(Publisher):
    """
    Acts as a publisher to a S3 bucket. Expects three properties in site
    configuration:
    * key: <YOUR AMAZON KEY>
    * secret: <YOUR AMAZON SECRET>
    * bucket: <bucket to upload data to>

    The publishers compares modification dates and only uploads files that
    have changed.
    """
    def initialize(self, settings):
        self.deploy_folder = self.site.config.deploy_root_path
        self.key = settings.key
        self.secret = settings.secret
        conn = S3Connection(self.key, self.secret)
        self.bucket = conn.create_bucket(settings.bucket)

    def publish(self):
        walker = self.deploy_folder.walker
        existing = dict([(k.key, k) for k in self.bucket.list()])
        for f in walker.walk_files():
            path = f.get_relative_path(self.deploy_folder.path)
            if path_separator == '\\':
                # S3 requires unix-style paths
                path = path.replace('\\', '/')
            k = existing.get(path)
            if not k:
                k = Key(self.bucket)
                k.key = path
            else:
                del existing[path]
                            
                tm_s = strptime(k.last_modified, "%Y-%m-%dT%H:%M:%S.000Z")
                last_modified = mktime(tm_s)
                if getmtime(f.path) <= last_modified:
                    logger.info("Skipping %s (not modified)" % f.path)
                    continue
            logger.info("Uploading %s" % f.path)
            k.set_contents_from_filename(f.path, replace=True)
        for k in existing.values():
            logger.info("Deleting %s" % k.path)
            k.delete()
