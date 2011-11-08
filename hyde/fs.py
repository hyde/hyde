# -*- coding: utf-8 -*-
"""
Unified object oriented interface for interacting with file system objects.
File system operations in python are distributed across modules: os, os.path,
fnamtch, shutil and distutils. This module attempts to make the right choices
for common operations to provide a single interface.
"""

import codecs
from datetime import datetime
import mimetypes
import os
import shutil
from distutils import dir_util
import functools
import fnmatch

from hyde.util import getLoggerWithNullHandler

logger = getLoggerWithNullHandler('fs')

# pylint: disable-msg=E0611


__all__ = ['File', 'Folder']


class FS(object):
    """
    The base file system object
    """

    def __init__(self, path):
        super(FS, self).__init__()
        if path == os.sep:
            self.path = path
        else:
            self.path = os.path.expandvars(os.path.expanduser(
                        unicode(path).strip().rstrip(os.sep)))

    def __str__(self):
        return self.path

    def __repr__(self):
        return self.path

    def __eq__(self, other):
        return unicode(self) == unicode(other)

    def __ne__(self, other):
        return unicode(self) != unicode(other)

    @property
    def fully_expanded_path(self):
        """
        Returns the absolutely absolute path. Calls os.(
        normpath, normcase, expandvars and expanduser).
        """
        return os.path.abspath(
        os.path.normpath(
        os.path.normcase(
        os.path.expandvars(
        os.path.expanduser(self.path)))))

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
        folder = self
        while folder.parent != stop:
            if folder.parent == folder:
                return
            yield folder.parent
            folder = folder.parent

    def is_descendant_of(self, ancestor):
        """
        Checks if this folder is inside the given ancestor.
        """
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
        if self.path == root:
            return ''
        ancestors = self.ancestors(stop=root)
        return functools.reduce(lambda f, p: Folder(p.name).child(f),
                                            ancestors,
                                            self.name)

    def get_mirror(self, target_root, source_root=None):
        """
        Returns a File or Folder object that reperesents if the entire
        fragment of this directory starting with `source_root` were copied
        to `target_root`.

        >>> Folder('/usr/local/hyde/stuff').get_mirror('/usr/tmp',
                                                source_root='/usr/local/hyde')
        Folder('/usr/tmp/stuff')
        """
        fragment = self.get_relative_path(
                        source_root if source_root else self.parent)
        return Folder(target_root).child(fragment)

    @staticmethod
    def file_or_folder(path):
        """
        Returns a File or Folder object that would represent the given path.
        """
        target = unicode(path)
        return Folder(target) if os.path.isdir(target) else File(target)

    def __get_destination__(self, destination):
        """
        Returns a File or Folder object that would represent this entity
        if it were copied or moved to `destination`.
        """
        if isinstance(destination, File) or os.path.isfile(unicode(destination)):
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

    @property
    def size(self):
        """
        Size of this file.
        """

        if not self.exists:
            return -1
        return os.path.getsize(self.path)

    @property
    def mimetype(self):
        """
        Gets the mimetype of this file.
        """
        (mime, _) = mimetypes.guess_type(self.path)
        return mime

    @property
    def is_binary(self):
        """Return true if this is a binary file."""
        with open(self.path, 'rb') as fin:
            CHUNKSIZE = 1024
            while 1:
                chunk = fin.read(CHUNKSIZE)
                if '\0' in chunk:
                    return True
                if len(chunk) < CHUNKSIZE:
                    break
        return False

    @property
    def is_text(self):
        """Return true if this is a text file."""
        return (not self.is_binary)

    @property
    def is_image(self):
        """Return true if this is an image file."""
        return self.mimetype.split("/")[0] == "image"


    @property
    def last_modified(self):
        """
        Returns a datetime object representing the last modified time.
        Calls os.path.getmtime.

        """
        return datetime.fromtimestamp(os.path.getmtime(self.path))

    def has_changed_since(self, basetime):
        """
        Returns True if the file has been changed since the given time.

        """
        return self.last_modified > basetime

    def older_than(self, another_file):
        """
        Checks if this file is older than the given file. Uses last_modified to
        determine age.

        """
        return self.last_modified < File(unicode(another_file)).last_modified

    @staticmethod
    def make_temp(text):
        """
        Creates a temprorary file and writes the `text` into it
        """
        import tempfile
        (handle, path) = tempfile.mkstemp(text=True)
        os.close(handle)
        afile = File(path)
        afile.write(text)
        return afile

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
        shutil.copy(self.path, unicode(destination))
        return target

    def delete(self):
        """
        Delete the file if it exists.
        """
        if self.exists:
            os.remove(self.path)


class FSVisitor(object):
    """
    Implements syntactic sugar for walking and listing folders
    """

    def __init__(self, folder, pattern=None):
        super(FSVisitor, self).__init__()
        self.folder = folder
        self.pattern = pattern

    def folder_visitor(self, function):
        """
        Decorator for `visit_folder` protocol
        """
        self.visit_folder = function
        return function

    def file_visitor(self, function):
        """
        Decorator for `visit_file` protocol
        """
        self.visit_file = function
        return function

    def finalizer(self, function):
        """
        Decorator for `visit_complete` protocol
        """
        self.visit_complete = function
        return function

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class FolderWalker(FSVisitor):
    """
    Walks the entire hirearchy of this directory starting with itself.

    If a pattern is provided, only the files that match the pattern are
    processed.
    """

    def walk(self, walk_folders=False, walk_files=False):
        """
        A simple generator that yields a File or Folder object based on
        the arguments.
        """

        if not walk_files and not walk_folders:
            return

        for root, _, a_files in os.walk(self.folder.path, followlinks=True):
            folder = Folder(root)
            if walk_folders:
                yield folder
            if walk_files:
                for a_file in a_files:
                    if (not self.pattern or
                        fnmatch.fnmatch(a_file, self.pattern)):
                        yield File(folder.child(a_file))

    def walk_all(self):
        """
        Yield both Files and Folders as the tree is walked.
        """

        return self.walk(walk_folders=True, walk_files=True)

    def walk_files(self):
        """
        Yield only Files.
        """
        return self.walk(walk_folders=False, walk_files=True)

    def walk_folders(self):
        """
        Yield only Folders.
        """
        return self.walk(walk_folders=True, walk_files=False)

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Automatically walk the folder when the context manager is exited.

        Calls self.visit_folder first and then calls self.visit_file for
        any files found. After all files and folders have been exhausted
        self.visit_complete is called.

        If visitor.visit_folder returns False, the files in the folder are not
        processed.
        """

        def __visit_folder__(folder):
            process_folder = True
            if hasattr(self, 'visit_folder'):
                process_folder = self.visit_folder(folder)
                # If there is no return value assume true
                #
                if process_folder is None:
                    process_folder = True
            return process_folder

        def __visit_file__(a_file):
            if hasattr(self, 'visit_file'):
                self.visit_file(a_file)

        def __visit_complete__():
            if hasattr(self, 'visit_complete'):
                self.visit_complete()

        for root, dirs, a_files in os.walk(self.folder.path, followlinks=True):
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
    Lists the contents of this directory.

    If a pattern is provided, only the files that match the pattern are
    processed.
    """

    def list(self, list_folders=False, list_files=False):
        """
        A simple generator that yields a File or Folder object based on
        the arguments.
        """

        a_files = os.listdir(self.folder.path)
        for a_file in a_files:
            path = self.folder.child(a_file)
            if os.path.isdir(path):
                if list_folders:
                    yield Folder(path)
            elif list_files:
                if not self.pattern or fnmatch.fnmatch(a_file, self.pattern):
                    yield File(path)

    def list_all(self):
        """
        Yield both Files and Folders as the folder is listed.
        """

        return self.list(list_folders=True, list_files=True)

    def list_files(self):
        """
        Yield only Files.
        """
        return self.list(list_folders=False, list_files=True)

    def list_folders(self):
        """
        Yield only Folders.
        """
        return self.list(list_folders=True, list_files=False)

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Automatically list the folder contents when the context manager
        is exited.

        Calls self.visit_folder first and then calls self.visit_file for
        any files found. After all files and folders have been exhausted
        self.visit_complete is called.
        """

        a_files = os.listdir(self.folder.path)
        for a_file in a_files:
            path = self.folder.child(a_file)
            if os.path.isdir(path) and hasattr(self, 'visit_folder'):
                self.visit_folder(Folder(path))
            elif hasattr(self, 'visit_file'):
                if not self.pattern or fnmatch.fnmatch(a_file, self.pattern):
                    self.visit_file(File(path))
        if hasattr(self, 'visit_complete'):
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
        return Folder(os.path.join(self.path, Folder(fragment).path))

    def child(self, fragment):
        """
        Returns a path of a child item represented by `fragment`.
        """
        return os.path.join(self.path, FS(fragment).path)

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
        shutil.copytree(self.path, unicode(target))
        return target

    def move_to(self, destination):
        """
        Moves this directory to the given destination. Returns a Folder object
        that represents the moved directory.
        """
        target = self.__get_destination__(destination)
        logger.info("Move %s to %s" % (self, target))
        shutil.move(self.path, unicode(target))
        return target

    def rename_to(self, destination_name):
        """
        Moves this directory to the given destination. Returns a Folder object
        that represents the moved directory.
        """
        target = self.parent.child_folder(destination_name)
        logger.info("Rename %s to %s" % (self, target))
        shutil.move(self.path, unicode(target))
        return target

    def _create_target_tree(self, target):
        """
        There is a bug in dir_util that makes `copy_tree` crash if a folder in
        the tree has been deleted before and readded now. To workaround the
        bug, we first walk the tree and create directories that are needed.
        """
        source = self
        with source.walker as walker:

            @walker.folder_visitor
            def visit_folder(folder):
                """
                Create the mirror directory
                """
                if folder != source:
                    Folder(folder.get_mirror(target, source)).make()

    def copy_contents_to(self, destination):
        """
        Copies the contents of this directory to the given destination.
        Returns a Folder object that represents the moved directory.
        """
        logger.info("Copying contents of %s to %s" % (self, destination))
        target = Folder(destination)
        target.make()
        self._create_target_tree(target)
        dir_util.copy_tree(self.path, unicode(target))
        return target

    def get_walker(self, pattern=None):
        """
        Return a `FolderWalker` object with a set pattern.
        """
        return FolderWalker(self, pattern)

    @property
    def walker(self):
        """
        Return a `FolderWalker` object
        """
        return FolderWalker(self)

    def get_lister(self, pattern=None):
        """
        Return a `FolderLister` object with a set pattern.
        """
        return FolderLister(self, pattern)

    @property
    def lister(self):
        """
        Return a `FolderLister` object
        """
        return FolderLister(self)
