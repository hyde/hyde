"""

Unified interface for performing file system tasks. Uses os, os.path. shutil
and distutil to perform the tasks. The behavior of some functions is slightly
contaminated with requirements from Hyde: For example, the backup function
deletes the directory that is being backed up.

"""
import os
import shutil
import codecs
import fnmatch
from datetime import datetime
# pylint: disable-msg=E0611
from distutils import dir_util, file_util

@staticmethod
def filter_hidden_inplace(item_list):
    """
    Given a list of filenames, removes filenames for invisible files (whose
    names begin with dots) or files whose names end in tildes '~'.
    Does not remove files with the filname '.htaccess'.
    The list is modified in-place; this function has no return value.
    """

    if not item_list:
        return

    wanted = filter(
        lambda item:
            not ((item.startswith('.') and item != ".htaccess")
                 or item.endswith('~')),
        item_list)

    count = len(item_list)
    good_item_count = len(wanted)

    if count == good_item_count:
        return

    item_list[:good_item_count] = wanted
    for _ in range(good_item_count, count):
        item_list.pop()

@staticmethod
def get_path_fragment(root_dir, a_dir):
    """
    Gets the path fragment starting at root_dir to a_dir
    """
    current_dir = a_dir
    current_fragment = ''
    while not current_dir == root_dir:
        (current_dir, current_fragment_part) = os.path.split(current_dir)
        current_fragment = os.path.join(
                            current_fragment_part, current_fragment)
    return current_fragment

@staticmethod
def get_mirror_dir(directory, source_root, mirror_root, ignore_root = False):
    """
    Returns the mirror directory from source_root to mirror_root
    """
    current_fragment = get_path_fragment(source_root, directory)

    if not current_fragment:
        return mirror_root

    mirror_directory = mirror_root
    if not ignore_root:
        mirror_directory = os.path.join(
                            mirror_root,
                            os.path.basename(source_root))

    mirror_directory = os.path.join(
                        mirror_directory, current_fragment)
    return mirror_directory


@staticmethod
def mirror_dir_tree(directory, source_root, mirror_root, ignore_root = False):
    """
    Create the mirror directory tree
    """

    mirror_directory = get_mirror_dir(
                        directory, source_root,
                        mirror_root, ignore_root)
    try:
        os.makedirs(mirror_directory)
    except os.error:
        pass
    return mirror_directory


class FileSystemEntity(object):
    """
    Base class for files and folders.
    """
    def __init__(self, path):
        super(FileSystemEntity, self).__init__()
        if path is FileSystemEntity:
            self.path = path.path
        else:
            self.path = path

    def __str__(self):
        return self.path

    def __repr__(self):
        return self.path

    def allow(self, include=None, exclude=None):
        """
        Given a set of wilcard patterns in the include and exclude arguments,
        tests if the patterns allow this item for processing.

        The exclude parameter is processed first as a broader filter and then
        include is used as a narrower filter to override the results for more
        specific files.

        Example:
        exclude = (".*", "*~")
        include = (".htaccess")

        """
        if not include:
            include = ()
        if not exclude:
            exclude = ()

        if reduce(lambda result,
         pattern: result or
            fnmatch.fnmatch(self.name, pattern), include, False):
            return True

        if reduce(lambda result, pattern:
            result and not fnmatch.fnmatch(self.name, pattern),
                exclude, True):
            return True

        return False

    @property
    def humblepath(self):
        """
        Expands variables, user, normalizes path and case and coverts
        to absolute.

        """
        return os.path.abspath(
        os.path.normpath(
        os.path.normcase(
        os.path.expandvars(
        os.path.expanduser(self.path)))))

    def same_as(self, other):
        """
        Checks if the path of this object is same as `other`. `other` must
        be a FileSystemEntity.

        """
        return (self.humblepath.rstrip(os.sep) ==
                        other.humblepath.rstrip(os.sep))

    @property
    def exists(self):
        """
        Checks if the entity exists in the file system.

        """
        return os.path.exists(self.path)

    @property
    def isdir(self):
        """
        Is this a folder.

        """
        return os.path.isdir(self.path)

    @property
    def stats(self):
        """
        Shortcut for os.stat.

        """

        return os.stat(self.path)

    @property
    def name(self):
        """
        Name of the entity. Calls os.path.basename.

        """

        return os.path.basename(self.path)

    @property
    def parent(self):
        """
        The parent folder. Returns a `Folder` object.

        """

        return Folder(os.path.dirname(self.path))

    def __get_destination__(self, destination):
        """
        Returns a File or Folder object that would represent this entity
        if it were copied or moved to `destination`. `destination` must be
        an instance of File or Folder.

        """
        if os.path.isdir(str(destination)):
            target = destination.child(self.name)
            if os.path.isdir(self.path):
                return Folder(target)
            else: return File(target)
        else:
            return destination

# pylint: disable-msg=R0904,W0142
class File(FileSystemEntity):
    """
    Encapsulates commonly used functions related to files.

    """
    def __init__(self, path):
        super(File, self).__init__(path)

    @property
    def size(self):
        """
        Gets the file size
        """
        return os.path.getsize(self.path)
        #return 1

    def has_extension(self, extension):
        """
        Checks if this file has the given extension.

        """
        return self.extension  == extension

    def delete(self):
        """
        Deletes if the file exists.

        """
        if self.exists:
            os.remove(self.path)

    @property
    def last_modified(self):
        """
        Returns a datetime object representing the last modified time.
        Calls os.path.getmtime.

        """
        return datetime.fromtimestamp(os.path.getmtime(self.path))

    def changed_since(self, basetime):
        """
        Returns True if the file has been changed since the given time.

        """
        return self.last_modified > basetime

    def older_than(self, another_file):
        """
        Checks if this file is older than the given file. Uses last_modified to
        determine age.

        """
        return another_file.last_modified > self.last_modified

    @property
    def path_without_extension(self):
        """
        The full path of the file without its extension.

        """
        return os.path.splitext(self.path)[0]

    @property
    def name_without_extension(self):
        """
        Name of the file without its extension.

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

    def move_to(self, destination):
        """
        Moves the file to the given destination. Returns a File
        object that represents the target file. `destination` must
        be a File or Folder object.

        """
        shutil.move(self.path, str(destination))
        return self.__get_destination__(destination)

    def copy_to(self, destination):
        """
        Copies the file to the given destination. Returns a File
        object that represents the target file. `destination` must
        be a File or Folder object.

        """
        shutil.copy(self.path, str(destination))
        return self.__get_destination__(destination)

    def write(self, text, encoding="utf-8"):
        """
        Writes the given text to the file using the given encoding.

        """

        fout = codecs.open(self.path, 'w', encoding)
        fout.write(text)
        fout.close()

    def read_all(self):
        """
        Reads from the file and returns the content as a string.

        """
        fin = codecs.open(self.path, 'r')
        read_text = fin.read()
        fin.close()
        return read_text

# pylint: disable-msg=R0904,W0142
class Folder(FileSystemEntity):
    """
    Encapsulates commonly used directory functions.

    """

    def __init__(self, path):
        super(Folder, self).__init__(path)

    def __str__(self):
        return self.path

    def __repr__(self):
        return self.path

    def delete(self):
        """
        Deletes the directory if it exists.

        """
        if self.exists:
            shutil.rmtree(self.path)

    def depth(self):
        """
        Returns the number of ancestors of this directory.

        """
        return len(self.path.split(os.sep))

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

    def is_parent_of(self, other_entity):
        """
        Returns True if this directory is a direct parent of the the given
        directory.

        """
        return self.same_as(other_entity.parent)

    def is_ancestor_of(self, other_entity):
        """
        Returns True if this directory is in the path of the given directory.
        Note that this will return True if the given directory is same as this.

        """
        folder = other_entity
        while not folder.parent.same_as(folder):
            folder = folder.parent
            if self.same_as(folder):
                return True
        return False

    def child(self, name):
        """
        Returns a path of a child item represented by `name`.

        """
        return os.path.join(self.path, name)

    def child_folder(self, *args):
        """
        Returns a Folder object by joining the path component in args
        to this directory's path.

        """
        return Folder(os.path.join(self.path, *args))

    def child_folder_with_fragment(self, fragment):
        """
        Returns a Folder object by joining the fragment to
        this directory's path.

        """
        return Folder(os.path.join(self.path, fragment.lstrip(os.sep)))

    def get_fragment(self, root):
        """
        Returns the path fragment of this directory starting with the given
        directory.

        """
        return get_path_fragment(str(root), self.path)

    def get_mirror_folder(self, root, mirror_root, ignore_root=False):
        """
        Returns a Folder object that reperesents if the entire fragment of this
        directory starting with `root` were copied to `mirror_root`. If ignore_root
        is True, the mirror does not include `root` directory itself.

        Example:
            Current Directory: /usr/local/hyde/stuff
            root: /usr/local/hyde
            mirror_root: /usr/tmp

        Result:

            if ignore_root == False:
                Folder(/usr/tmp/hyde/stuff)
            if ignore_root == True:
                Folder(/usr/tmp/stuff)

        """
        path = get_mirror_dir(self.path,
                    str(root), str(mirror_root), ignore_root)
        return Folder(path)

    def create_mirror_folder(self, root, mirror_root, ignore_root=False):
        """
        Creates the mirror directory returned by `get_mirror_folder`

        """
        mirror_folder = self.get_mirror_folder(
                        root, mirror_root, ignore_root)
        mirror_folder.make()
        return mirror_folder

    def backup(self, destination):
        """
        Creates a backup of this directory in the given destination. The backup is
        suffixed with a number for uniqueness. Deletes this directory after backup
        is complete.

        """
        new_name = self.name
        count = 0
        dest = Folder(destination.child(new_name))
        while(True):
            dest = Folder(destination.child(new_name))
            if not dest.exists:
                break
            else:
                count = count + 1
                new_name = self.name + str(count)
        dest.make()
        dest.move_contents_of(self)
        self.delete()
        return dest

    def move_to(self, destination):
        """
        Moves this directory to the given destination. Returns a Folder object
        that represents the moved directory.

        """
        shutil.copytree(self.path, str(destination))
        shutil.rmtree(self.path)
        return self.__get_destination__(destination)

    def copy_to(self, destination):
        """
        Copies this directory to the given destination. Returns a Folder object
        that represents the moved directory.

        """
        shutil.copytree(self.path, str(destination))
        return self.__get_destination__(destination)

    def move_folder_from(self, source, incremental=False):
        """
        Moves the given source directory to this directory. If incremental is True
        only newer objects are overwritten.

        """
        self.copy_folder_from(source, incremental)
        shutil.rmtree(str(source))

    def copy_folder_from(self, source, incremental=False):
        """
        Copies the given source directory to this directory. If incremental is True
        only newer objects are overwritten.

        """
        # There is a bug in dir_util that makes copy_tree crash if a folder in
        # the tree has been deleted before and readded now. To workaround the
        # bug, we first walk the tree and create directories that are needed.
        #
        # pylint: disable-msg=C0111,W0232
        target_root = self
        # pylint: disable-msg=R0903
        class _DirCreator:
            @staticmethod
            def visit_folder(folder):
                target = folder.get_mirror_folder(
                            source.parent, target_root, ignore_root=True)
                target.make()

        source.walk(_DirCreator)

        dir_util.copy_tree(str(source),
                        self.child(source.name),
                        update=incremental)

    def move_contents_of(self, source, move_empty_folders=True,
                        incremental=False):
        """
        Moves the contents of the given source directory to this directory. If
        incremental is True only newer objects are overwritten.

        """
        # pylint: disable-msg=C0111,W0232
        class _Mover:
            @staticmethod
            def visit_folder(folder):
                self.move_folder_from(folder, incremental)
            @staticmethod
            def visit_file(a_file):
                self.move_file_from(a_file, incremental)
        source.list(_Mover, move_empty_folders)

    def copy_contents_of(self, source, copy_empty_folders=True,
                        incremental=False):
        """
        Copies the contents of the given source directory to this directory. If
        incremental is True only newer objects are overwritten.

        """
        # pylint: disable-msg=C0111,W0232
        class _Copier:
            @staticmethod
            def visit_folder(folder):
                self.copy_folder_from(folder, incremental)
            @staticmethod
            def visit_file(a_file):
                self.copy_file_from(a_file, incremental)
        source.list(_Copier, copy_empty_folders)

    def move_file_from(self, source, incremental=False):
        """
        Moves the given source file to this directory. If incremental is True the
        move is performed only if the source file is newer.

        """
        self.copy_file_from(source, incremental)
        source.delete()

    def copy_file_from(self, source, incremental=False):
        """
        Copies the given source file to this directory. If incremental is True the
        move is performed only if the source file is newer.

        """
        file_util.copy_file(str(source), self.path, update=incremental)

    def list(self, visitor, list_empty_folders=True):
        """
        Calls the visitor.visit_file or visitor.visit_folder for each file or folder
        in this directory. If list_empty_folders is False folders that are empty are
        skipped.
        """
        a_files = os.listdir(self.path)
        for a_file in a_files:
            path = os.path.join(self.path, str(a_file))
            if os.path.isdir(path):
                if not list_empty_folders:
                    if Folder(path).empty():
                        continue
                visitor.visit_folder(Folder(path))
            else:
                visitor.visit_file(File(path))

    def empty(self):
        """
        Checks if this directory or any of its subdirectories contain files.

        """
        paths = os.listdir(self.path)
        for path in paths:
            if os.path.isdir(path):
                if not Folder(path).empty():
                    return False
            else:
                return False
        return True

    def walk(self, visitor = None, pattern = None):
        """
        Walks the entire hirearchy of this directory starting with itself.
        Calls visitor.visit_folder first and then calls visitor.visit_file for
        any files found. After all files and folders have been exhausted
        visitor.visit_complete is called.

        If a pattern is provided, only the files that match the pattern are
        processed.

        If visitor.visit_folder returns False, the files in the folder are not
        processed.

        """
        def __visit_folder__(visitor, folder):
            process_folder = True
            if visitor and hasattr(visitor,'visit_folder'):
                process_folder = visitor.visit_folder(folder)
                # If there is no return value assume true
                #
                if process_folder is None:
                    process_folder = True
            return process_folder

        def __visit_file__(visitor, a_file):
            if visitor and hasattr(visitor,'visit_file'):
                visitor.visit_file(a_file)

        def __visit_complete__(visitor):
            if visitor and hasattr(visitor,'visit_complete'):
                visitor.visit_complete()

        for root, dirs, a_files in os.walk(self.path):
            folder = Folder(root)
            if not __visit_folder__(visitor, folder):
                dirs[:] = []
                continue
            for a_file in a_files:
                if not pattern or fnmatch.fnmatch(a_file, pattern):
                    __visit_file__(visitor, File(folder.child(a_file)))
        __visit_complete__(visitor)