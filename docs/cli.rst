======================
Command Line Reference
======================

The ``hyde`` command line supports the following subcommands:

.. TODO: This is a really good candidate for an autoclass.

+-------------+---------------------------------------------------------+
| ``create``  | Initialize a new site at a given path.                  |
+-------------+---------------------------------------------------------+
| ``gen``     | Generate the website to a configured deploy folder.     |
+-------------+---------------------------------------------------------+
| ``serve``   | Start a local HTTP server that regenerates based on the |
|             | requested file.                                         |
+-------------+---------------------------------------------------------+
| ``publish`` | Publish the generated site based on configuration.      |
+-------------+---------------------------------------------------------+


create
======

Create a new Hyde website::

    hyde create

    hyde [-s </site/path>] [-v] create [-l <layout>] [-f] [-h]

Options:

``-s SITEPATH``, ``--sitepath SITEPATH``

Specify where the site should be created.

A new site will only be created if ``SITEPATH`` does not exist. To overwrite an
existing directory, use the ``--force`` option.

Defaults to the current directory.

----

``-f``, ``--force``

Overwrite files and folders at the given site path.

``hyde create`` will raise an exception if the target directory is not empty
unless this option is specified.

Defaults to false.

----

``-l LAYOUT``, ``--layout LAYOUT``

The name of the layout to use for creating the initial site. Hyde provides
three layouts: ``basic``, ``test``, and ``doc``.

Hyde tries to locate the specified layout in the following folders:

1. In the ``layouts`` folder under the path specified by the ``HYDE_DATA``
   environment variable.
2. In ``hyde``'s own ``layouts`` folder.

Assuming the ``HYDE_DATA`` environment variable is empty and the folder
``~/test`` is empty, the following command will create a new Hyde site at
``~/test`` with the contents of the ``layouts/doc`` folder::

    hyde -s ~/test create -l doc

Defaults to ``basic``.

----

``-v``, ``--verbose``

Log detailed messages to the console.

Defaults to false. Show only essential messages if this option is omitted.

----

``-h``, ``--help``

Display the help text for the ``create`` command.


generate
========

Generate the given website::

    hyde gen

    hyde [-s <site/path>] [-v] gen [-r] [-d <deploy/path>] [-c <config/path>] [-h]

Options:

``-s SITEPATH``, ``--sitepath SITEPATH``

The path to the site to be generated.th to the site to be generated.

Defaults to the current directory.

----

``-r``, ``regen``

Regenerate the entire website. By default, ``hyde gen`` performs incremental
generation. While Hyde does a good job at understanding dependencies, its far
from perfect. When there are cases where the incremental generation does not
yield the desired results, you can provide this option to generate the website
from scratch.

Defaults to incremental generation.

----

``-d DEPLOY_PATH``, ``--deploy-path DEPLOY_PATH``

Location where the site should be generated. This option overrides any setting
specified in the Hyde `configuration <config>`_. The path is assumed to be
relative to the site path unless a preceding path separator is found.

Defaults to the option specified in the config file or the ``deploy`` folder
under the current site path if no config entry exists.

----

``-c CONFIG``, ``--config-path CONFIG``

Specify an alternate configuration file to use for generating the site. This is
useful if you have two different configurations for you production versus
development websites. The path is assumed to be relative to the site path
unless a preceding path separator is found.

The following command will use ``production.yaml`` as the configuration file
and generate the website at ``~/test`` to the ``~/production_site`` directory::

    cd ~/test
    hyde gen -c production.yaml -d ~/production_site

Defaults to ``site.yaml``.

----

``-v``, ``--verbose``

Log detailed messages to the console.

Defaults to false. Show only essential messages if this option is omitted.

----

``-h``, ``--help``

Display the help text for the ``gen`` command.


serve
=====

Start the built in web server that also regenerates based on the request if
there are changes::

    hyde serve

    hyde [-s </site/path>] [-v] gen [-d </deploy/path>] [-c <config/path>] [-h]

Options:

``-s SITEPATH``, ``--sitepath SITEPATH``
``-d DEPLOY_PATH``, ``--deploy-path DEPLOY_PATH``
``-c CONFIG``, ``--config-path CONFIG``

Since the ``serve`` command auto generates if there is a need, it needs the
same parameters as the ``gen`` command. The above parameters serve the same
purpose here as in the ``gen`` command.

----

``-a ADDRESS``, ``--address ADDRESS``

The address to serve the website.

Defaults to ``localhost``.

----

``-p PORT``, ``--port PORT``

The port to serve the website.

The following command will serve the website at http://localhost:8181::

    hyde serve -p 8181

Defaults to 8080.

----

``-h``, ``--help``

Display the help text for the ``serve`` command.


publish
=======

Publish the site based on configuration. Currently, the only supported
publishing target is a git repository. See the `publisher documentation
<publisher>`_ for more information.

Options:

``-s SITEPATH``, ``--sitepath SITEPATH``

The path to the site to be generated.

Defaults to the current working directory.

----

``-p CONFIG``

The key for  configuration section in the site configuration that has the
settings for the publisher. For example, the following configuration, when
invoked with ``hyde publish -p github`` will use the ``Git`` publisher to
publish the generated site to ``hyde/hyde.github.com`` repository::

    publisher:
        github:
            type: hyde.ext.publishers.dvcs.Git
            path: ../hyde.github.com
            url: git@github.com:hyde/hyde.github.com.git
