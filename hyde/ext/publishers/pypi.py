"""
Contains classes and utilities that help publishing a hyde website to
the documentation hosting on http://packages.python.org/.

"""

import os
import getpass
import zipfile
import tempfile
import httplib
import urlparse
from base64 import standard_b64encode
import ConfigParser

from hyde.publisher import Publisher

from commando.util import getLoggerWithNullHandler
logger = getLoggerWithNullHandler('hyde.ext.publishers.pypi')




class PyPI(Publisher):

    def initialize(self, settings):
        self.settings = settings
        self.project = settings.project
        self.url = getattr(settings,"url","https://pypi.python.org/pypi/")
        self.username = getattr(settings,"username",None)
        self.password = getattr(settings,"password",None)
        self.prompt_for_credentials()

    def prompt_for_credentials(self):
        pypirc_file = os.path.expanduser("~/.pypirc")
        if not os.path.isfile(pypirc_file):
            pypirc = None
        else:
            pypirc = ConfigParser.RawConfigParser()
            pypirc.read([pypirc_file])
        missing_errs = (ConfigParser.NoSectionError,ConfigParser.NoOptionError)
        #  Try to find username in .pypirc
        if self.username is None:
            if pypirc is not None:
                try:
                    self.username = pypirc.get("server-login","username")
                except missing_errs:
                    pass
        #  Prompt for username on command-line
        if self.username is None:
            print "Username: ",
            self.username = raw_input().strip()
        #  Try to find password in .pypirc
        if self.password is None:
            if pypirc is not None:
                try:
                    self.password = pypirc.get("server-login","password")
                except missing_errs:
                    pass
        #  Prompt for username on command-line
        if self.password is None:
            self.password = getpass.getpass("Password: ")
        #  Validate the values.
        if not self.username:
            raise ValueError("PyPI requires a username")
        if not self.password:
            raise ValueError("PyPI requires a password")

    def publish(self):
        super(PyPI, self).publish()
        tf = tempfile.TemporaryFile()
        try:
            #  Bundle it up into a zipfile
            logger.info("building the zipfile")
            root = self.site.config.deploy_root_path
            zf = zipfile.ZipFile(tf,"w",zipfile.ZIP_DEFLATED)
            try:
                for item in root.walker.walk_files():
                    logger.info("  adding file: %s",item.path)
                    zf.write(item.path,item.get_relative_path(root))
            finally:
                zf.close()
            #  Formulate the necessary bits for the HTTP POST.
            #  Multipart/form-data encoding.  Yuck.
            authz = self.username + ":" + self.password
            authz = "Basic " + standard_b64encode(authz)
            boundary = "-----------" + os.urandom(20).encode("hex")
            sep_boundary = "\r\n--" + boundary
            end_boundary = "\r\n--" + boundary + "--\r\n"
            content_type = "multipart/form-data; boundary=%s" % (boundary,)
            items = ((":action","doc_upload"),("name",self.project))
            body_prefix = ""
            for (name,value) in items:
                body_prefix += "--" + boundary + "\r\n"
                body_prefix += "Content-Disposition: form-data; name=\""
                body_prefix += name + "\"\r\n\r\n"
                body_prefix += value + "\r\n"
            body_prefix += "--" + boundary + "\r\n"
            body_prefix += "Content-Disposition: form-data; name=\"content\""
            body_prefix += "; filename=\"website.zip\"\r\n\r\n"
            body_suffix = "\r\n--" + boundary + "--\r\n"
            content_length = len(body_prefix) + tf.tell() + len(body_suffix)
            #  POST it up to PyPI
            logger.info("uploading to PyPI")
            url = urlparse.urlparse(self.url)
            if url.scheme == "https":
                con = httplib.HTTPSConnection(url.netloc)
            else:
                con = httplib.HTTPConnection(url.netloc)
            con.connect()
            try:
                con.putrequest("POST", self.url)
                con.putheader("Content-Type",content_type)
                con.putheader("Content-Length",str(content_length))
                con.putheader("Authorization",authz)
                con.endheaders()
                con.send(body_prefix)
                tf.seek(0)
                data = tf.read(1024*32)
                while data:
                    con.send(data)
                    data = tf.read(1024*32)
                con.send(body_suffix)
                r = con.getresponse()
                try:
                    #  PyPI tries to redirect to the page on success.
                    if r.status in (200,301,):
                        logger.info("success!")
                    else:
                        msg = "Upload failed: %s %s" % (r.status,r.reason,)
                        raise Exception(msg)
                finally:
                    r.close()
            finally:
                con.close()
        finally:
            tf.close()


