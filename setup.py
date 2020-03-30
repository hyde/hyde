from setuptools import setup, find_packages
from hyde.version import __version__

from distutils.util import convert_path
from fnmatch import fnmatchcase
import os
import sys


PROJECT = 'hyde'


def get_content(*filenames): # TODO: add typhint in version 1.0.0
    """Takes in an aribtrary amount of file paths and scrapes the content from the files

    Parameters
    ----------
    filenames: str
        The paths to the files
    
    Returns
    -------
    str
        The content of the files
    """
    content = ""
    for file in filenames:
        with open(file, "r") as full_description:
            content += full_description.read()
    return content



# TODO: Look at removing find_package_data() with https://setuptools.readthedocs.io/en/latest/setuptools.html#basic-use
##############################################################################
# find_package_data is an Ian Bicking creation.

# Provided as an attribute, so you can append to these instead
# of replicating them:
standard_exclude = ('*.py', '*.pyc', '*~', '.*', '*.bak', '*.swp*')
standard_exclude_directories = ('.*', 'CVS', '_darcs', './build',
                                './dist', 'EGG-INFO', '*.egg-info')


def find_package_data(
        where='.', package='',
        exclude=standard_exclude,
        exclude_directories=standard_exclude_directories,
        only_in_packages=True,
        show_ignored=False):
    """
    Return a dictionary suitable for use in ``package_data``
    in a distutils ``setup.py`` file.

    The dictionary looks like::

        {'package': [files]}

    Where ``files`` is a list of all the files in that package that
    don't match anything in ``exclude``.

    If ``only_in_packages`` is true, then top-level directories that
    are not packages won't be included (but directories under packages
    will).

    Directories matching any pattern in ``exclude_directories`` will
    be ignored; by default directories with leading ``.``, ``CVS``,
    and ``_darcs`` will be ignored.

    If ``show_ignored`` is true, then all the files that aren't
    included in package data are shown on stderr (for debugging
    purposes).

    Note patterns use wildcards, or can be exact paths (including
    leading ``./``), and all searching is case-insensitive.

    This function is by Ian Bicking.
    """

    out = {}
    stack = [(convert_path(where), '', package, only_in_packages)]
    while stack:
        where, prefix, package, only_in_packages = stack.pop(0)
        for name in os.listdir(where):
            fn = os.path.join(where, name)
            if os.path.isdir(fn):
                bad_name = False
                for pattern in exclude_directories:
                    if fnmatchcase(name, pattern) or \
                       fn.lower() == pattern.lower():

                        bad_name = True
                        if show_ignored:
                            msg = "Directory {} ignored by pattern {}"
                            sys.stderr.write(msg.format(fn, pattern))
                        break
                if bad_name:
                    continue
                if os.path.isfile(os.path.join(fn, '__init__.py')):
                    if not package:
                        new_package = name
                    else:
                        new_package = package + '.' + name
                    stack.append((fn, '', new_package, False))
                else:
                    stack.append((fn, prefix + name + '/', package,
                                  only_in_packages))
            elif package or not only_in_packages:
                # is a file
                bad_name = False
                for pattern in exclude:
                    if fnmatchcase(name, pattern) \
                       or fn.lower() == pattern.lower():

                        bad_name = True
                        if show_ignored:
                            msg = "File {} ignored by pattern {}"
                            sys.stderr.write(msg.format(fn, pattern))
                        break
                if bad_name:
                    continue
                out.setdefault(package, []).append(prefix+name)
    return out

##############################################################################


def read_requirements(*filenames):
    """Takes an arbitrary number of filepaths and returns a list of the
    requirements in the file (newline delimited).

    Returns
    -------
    list:
        The list of requirements to install
    """
    reqs = []   # list of requirements built from the files
    for file in filenames:
        with open(file, "r") as requirements_file:
            reqs = [req.split('#', 1)[0].strip() for req in requirements_file]
            reqs = [req for req in reqs if req]
    return reqs


install_requires = read_requirements('requirements.txt') # Defines general Hyde dependencies
dev_requires = read_requirements('dev-only.txt')         # Defines development dependencies

setup(name=PROJECT,
    version=__version__,
    description='hyde is a static website generator',
    long_description=get_content('README.rst', 'CHANGELOG.rst'),
    author='hyde developers',
    author_email='hyde-dev@googlegroups.com',
    url='http://hyde.github.io',
    packages=find_packages(),
    requires=['python (>= 2.7)'],
    install_requires=install_requires,
    tests_require=dev_requires,
    test_suite='nose.collector',
    include_package_data=True,
    # Scan the input for package information
    # to grab any data files (text, images, etc.)
    # associated with sub-packages.

    package_data=find_package_data(PROJECT,
                                    package=PROJECT,
                                    only_in_packages=False,),
    entry_points={
        'console_scripts': [
            'hyde = hyde.main:main'
        ]
    },
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Code Generators',
        'Topic :: Internet',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
    ],
    zip_safe=False,)
