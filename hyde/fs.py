# -*- coding: utf-8 -*-
"""
Unified object oriented interface for interacting with file system objects. File system operations in
python are distributed across modules: os, os.path, fnamtch, shutil and distutils. This module attempts
to make the right choices for common operations to provide a single interface.
"""

import codecs
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
    def parent(self):
        """
        The parent folder. Returns a `Folder` object.
        """
        return Folder(os.path.dirname(self.path))

class File(FS):
    """
    The File object.
    """
    def __init__(self, path):
        super(File, self).__init__(path)

    @property
    def name_without_extension(self):
        """
        Returns the name of the FS object without its extension
        """
        return os.path.splitext(self.name)[0]

    @property
    def extension(self):
        """
        File extension prefixed with a dot.
        """
        return os.path.splitext(self.path)[1]

    @property
    def kind(self):
        """
        File extension without dot prefix.
        """
        return self.extension.lstrip(".")

    def read_all(self, encoding='utf-8'):
        """
        Reads from the file and returns the content as a string.
        """
        with codecs.open(self.path, 'r', encoding) as fin:
            read_text = fin.read()
        return read_text


class Folder(FS):
    """
    Represents a directory.
    """
    def __init__(self, path):
        super(Folder, self).__init__(path)

    def child_folder(self, fragment):
        """
        Returns a folder object by combining the fragment to this folder's path
        """
        return Folder(os.path.join(self.path, fragment))

    def child(self, name):
        """
        Returns a path of a child item represented by `name`.
        """
        return os.path.join(self.path, name)