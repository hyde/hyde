# -*- coding: utf-8 -*-
"""
Unified object oriented interface for interacting with file system objects.
File system operations in python are distributed across modules: os, os.path,
fnamtch, shutil and distutils. This module attempts to make the right choices
for common operations to provide a single interface.
"""

import codecs
# import fnmatch
import os
import shutil
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

    def __eq__(self, other):
        return str(self) == str(other)

    def __ne__(self, other):
        return str(self) != str(other)

    @property
    def exists(self):
        """
        Does the file system object exist?
        """
        return os.path.exists(self.path)

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


    @staticmethod
    def file_or_folder(path):
        """
        Returns a File or Folder object that would represent the given path.
        """
        target = str(path)
        return Folder(target) if os.path.isdir(target) else File(target)

    def __get_destination__(self, destination):
        """
        Returns a File or Folder object that would represent this entity
        if it were copied or moved to `destination`. `destination` must be
        an instance of File or Folder.
        """
        if os.path.isdir(str(destination)):
            return FS.file_or_folder(Folder(destination).child(self.name))
        else:
            return destination


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

    def write(self, text, encoding="utf-8"):
        """
        Writes the given text to the file using the given encoding.
        """
        with codecs.open(self.path, 'w', encoding) as fout:
            fout.write(text)

    def copy_to(self, destination):
        """
        Copies the file to the given destination. Returns a File
        object that represents the target file. `destination` must
        be a File or Folder object.
        """
        shutil.copy(self.path, str(destination))
        return self.__get_destination__(destination)


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

    def make(self):
        """
        Creates this directory and any of the missing directories in the path.
        Any errors that may occur are eaten.
        """
        try:
            if not self.exists:
                os.makedirs(self.path)
        except os.error:
            pass
        return self

    def delete(self):
        """
        Deletes the directory if it exists.
        """
        if self.exists:
            shutil.rmtree(self.path)

    def copy_to(self, destination):
        """
        Copies this directory to the given destination. Returns a Folder object
        that represents the moved directory.
        """
        target = self.__get_destination__(destination)
        shutil.copytree(self.path, str(target))
        return target