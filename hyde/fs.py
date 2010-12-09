"""
Unified object oriented interface for interacting with file system objects. File system operations in
python are distributed across modules: os, os.path, fnamtch, shutil and distutils. This module attempts
to make the right choices for common operations to provide a single interface.
"""

# import codecs
# import fnmatch
import os
# import shutil
# from datetime import datetime

# pylint: disable-msg=E0611
# from distutils import dir_util, file_util

class FS(object):
    """
    The base file system object
    """
    def __init__(self, path):
        super(FS, self).__init__()
        self.path = str(path)

    def __str__(self):
        return self.path

    def __repr__(self):
        return self.path

    @property
    def name(self):
        """
        Returns the name of the FS object with its extension
        """
        return os.path.basename(self.path)

    @property
    def name_without_extension(self):
        """
        Returns the name of the FS object without its extension
        """
        return os.path.splitext(self.name)[0]

    @property
    def extension(self):
        """
        File's extension prefixed with a dot.
        """
        return os.path.splitext(self.path)[1]

    @property
    def kind(self):
        """
        File's extension without a dot prefix.
        """
        return self.extension.lstrip(".")