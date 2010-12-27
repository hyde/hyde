# -*- coding: utf-8 -*-
"""
Unified object oriented interface for interacting with file system objects.
File system operations in python are distributed across modules: os, os.path,
fnamtch, shutil and distutils. This module attempts to make the right choices
for common operations to provide a single interface.
"""

import codecs
import contextlib
import logging
from logging import NullHandler
import os
import shutil
from distutils import dir_util
import functools
import itertools
# pylint: disable-msg=E0611

logger = logging.getLogger('fs')
logger.addHandler(NullHandler())


__all__ = ['File', 'Folder']

class FS(object):
    """
    The base file system object
    """
    def __init__(self, path):
        super(FS, self).__init__()
        self.path = str(path).strip().rstrip(os.sep)

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

    @property
    def depth(self):
        """
        Returns the number of ancestors of this directory.
        """
        return len(self.path.rstrip(os.sep).split(os.sep))


    def ancestors(self, stop=None):
        """
        Generates the parents until stop or the absolute
        root directory is reached.
        """
        f = self
        while f.parent != stop:
            if f.parent == f:
                return
            yield f.parent
            f = f.parent

    def is_descendant_of(self, ancestor):
         stop = Folder(ancestor)
         for folder in self.ancestors():
             if folder == stop:
                 return True
             if stop.depth > folder.depth:
                 return False
         return False

    def get_relative_path(self, root):
        """
        Gets the fragment of the current path starting at root.
        """
        return functools.reduce(lambda f, p: Folder(p.name).child(f), self.ancestors(stop=root), self.name)

    def get_mirror(self, target_root, source_root=None):
        """
        Returns a File or Folder object that reperesents if the entire fragment of this
        directory starting with `source_root` were copied to `target_root`.

        >>> Folder('/usr/local/hyde/stuff').get_mirror('/usr/tmp', source_root='/usr/local/hyde')
        Folder('/usr/tmp/stuff')
        """
        fragment = self.get_relative_path(source_root if source_root else self.parent)
        return Folder(target_root).child(fragment)

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
        if it were copied or moved to `destination`.
        """
        if (isinstance(destination, File) or os.path.isfile(str(destination))):
            return destination
        else:
            return FS.file_or_folder(Folder(destination).child(self.name))

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
        logger.info("Reading everything from %s" % self)
        with codecs.open(self.path, 'r', encoding) as fin:
            read_text = fin.read()
        return read_text

    def write(self, text, encoding="utf-8"):
        """
        Writes the given text to the file using the given encoding.
        """
        logger.info("Writing to %s" % self)
        with codecs.open(self.path, 'w', encoding) as fout:
            fout.write(text)

    def copy_to(self, destination):
        """
        Copies the file to the given destination. Returns a File
        object that represents the target file. `destination` must
        be a File or Folder object.
        """
        target = self.__get_destination__(destination)
        logger.info("Copying %s to %s" % (self, target))
        shutil.copy(self.path, str(destination))
        return target

class FSVisitor(object):
    """
    Implements syntactic sugar for walking and listing folders
    """

    def __init__(self, folder, pattern=None):
        super(FSVisitor, self).__init__()
        self.folder = folder
        self.pattern = pattern

    def folder_visitor(self, f):
        """
        Decorator for `visit_folder` protocol
        """
        self.visit_folder = f
        return f

    def file_visitor(self, f):
        """
        Decorator for `visit_file` protocol
        """
        self.visit_file = f
        return f

    def finalizer(self, f):
        """
        Decorator for `visit_complete` protocol
        """
        self.visit_complete = f
        return f

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb): pass


class FolderWalker(FSVisitor):
    """
    Walks the entire hirearchy of this directory starting with itself.
    Calls self.visit_folder first and then calls self.visit_file for
    any files found. After all files and folders have been exhausted
    self.visit_complete is called.

    If a pattern is provided, only the files that match the pattern are
    processed.

    If visitor.visit_folder returns False, the files in the folder are not
    processed.
    """

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Automatically walk the folder when the context manager is exited.
        """

        def __visit_folder__(folder):
            process_folder = True
            if hasattr(self,'visit_folder'):
                process_folder = self.visit_folder(folder)
                # If there is no return value assume true
                #
                if process_folder is None:
                    process_folder = True
            return process_folder

        def __visit_file__(a_file):
            if hasattr(self,'visit_file'):
                self.visit_file(a_file)

        def __visit_complete__():
            if hasattr(self,'visit_complete'):
                self.visit_complete()

        for root, dirs, a_files in os.walk(self.folder.path):
            folder = Folder(root)
            if not __visit_folder__(folder):
                dirs[:] = []
                continue
            for a_file in a_files:
                if not self.pattern or fnmatch.fnmatch(a_file, self.pattern):
                    __visit_file__(File(folder.child(a_file)))
        __visit_complete__()


class FolderLister(FSVisitor):
    """
    Lists the contents of this directory starting with itself.
    Calls self.visit_folder first and then calls self.visit_file for
    any files found. After all files and folders have been exhausted
    self.visit_complete is called.

    If a pattern is provided, only the files that match the pattern are
    processed.
    """

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Automatically list the folder contents when the context manager is exited.
        """

        a_files = os.listdir(self.folder.path)
        for a_file in a_files:
            path = self.folder.child(a_file)
            if os.path.isdir(path) and hasattr(self, 'visit_folder'):
                self.visit_folder(Folder(path))
            elif hasattr(self, 'visit_file'):
                if not self.pattern or fnmatch.fnmatch(a_file, self.pattern):
                    self.visit_file(File(path))
        if hasattr(self,'visit_complete'):
            self.visit_complete()

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
                logger.info("Creating %s" % self.path)
                os.makedirs(self.path)
        except os.error:
            pass
        return self

    def delete(self):
        """
        Deletes the directory if it exists.
        """
        if self.exists:
            logger.info("Deleting %s" % self.path)
            shutil.rmtree(self.path)

    def copy_to(self, destination):
        """
        Copies this directory to the given destination. Returns a Folder object
        that represents the moved directory.
        """
        target = self.__get_destination__(destination)
        logger.info("Copying %s to %s" % (self, target))
        shutil.copytree(self.path, str(target))
        return target

    def _create_target_tree(self, target):
        """
        There is a bug in dir_util that makes `copy_tree` crash if a folder in
        the tree has been deleted before and readded now. To workaround the
        bug, we first walk the tree and create directories that are needed.
        """
        with self.walk() as walker:
            @walker.folder_visitor
            def visit_folder(folder):
                """
                Create the mirror directory
                """
                Folder(folder.get_mirror(target)).make()

    def copy_contents_to(self, destination):
        """
        Copies the contents of this directory to the given destination.
        Returns a Folder object that represents the moved directory.
        """
        logger.info("Copying contents of %s to %s" % (self, destination))
        self._create_target_tree(Folder(destination))
        dir_util.copy_tree(self.path, str(destination))
        return Folder(destination)

    def walk(self, pattern=None):
        """
        Walks this folder using `FolderWalker`
        """

        return FolderWalker(self, pattern)

    def list(self, pattern=None):
        """
        Lists this folder using `FolderLister`
        """

        return FolderLister(self, pattern)