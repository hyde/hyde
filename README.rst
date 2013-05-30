Version 0.8.7

A brand new **hyde**
====================

This is the new version of `hyde`_ under active development.
`Hyde documentation`_ is a work in progress.

`Hyde starter kit`_ by `merlinrebrovic`_ is a really nice way to get started
with hyde.

`Hyde layout for bootstrap`_ by `auzigog`_ is also a good alternative if you
like Twitter's `bootstrap framework`_.

You can also take a look at `Hyde Powered Websites`_ for inspiration and reference.

Installation
------------

To get the latest released version:

::

    pip install hyde

For the current trunk:

::

    pip install -e git://github.com/hyde/hyde.git#egg=hyde

Creating a new hyde site
------------------------

The following command:

::

        hyde -s ~/test_site create

will create a new hyde site using the test layout.

Generating the hyde site
------------------------

::

        cd ~/test_site
        hyde gen

Serving the website
-------------------

::

        cd ~/test_site
        hyde serve
        open http://localhost:8080

Publishing the website
----------------------

::

        cd ~/test_site
        hyde publish -p github


Hyde supports extensible publishers.

Github
~~~~~~~

The hyde documentation is published to github pages using this command with
the following configuration:

::

        publisher:
            github:
                type: hyde.ext.publishers.dvcs.Git
                path: ../hyde.github.com
                url: git@github.com:hyde/hyde.github.com.git

.. Note:: Currently, the initial path must have clone of the repository
          already in place for this command to work.

PyFS
~~~~~~~

Hyde also has a publisher that acts as a frontend to the awesome
`PyFS library`_ (thanks to `rfk`_). Here are a few configuration
options for some PyFS backends:

::

        publisher:
            zip:
                type: hyde.ext.publishers.pyfs.PyFS
                url: zip://~/deploy/hyde/docs.zip
            s3:
                type: hyde.ext.publishers.pyfs.PyFS
                url: s3://hyde/docs
            sftp:
                type: hyde.ext.publishers.pyfs.PyFS
                url: sftp:hydeuser:hydepassword@hydedocs.org

.. Note:: PyFS is not installed with hyde. In order to use the
          PyFS publisher, you need to install pyfs separately.

Any PyFS dependencies (Example: `boto` for S3 publishing)
need to be installed separately as well.

::

        pip install fs
        pip install boto

To get additional help on PyFS backends, you can run the following
command once PyFS is installed:

::

        fsls --listopeners

Examples
--------

1. `Hyde Documentation Source`_
2. `Cloudpanic`_
3. `Ringce`_

A brief list of features
--------------------------

1. Evented Plugins: The Plugin hooks allow plugins to listen to events
   that occur during different times in the lifecycle and respond
   accordingly.
2. Metadata: Hyde now supports hierarchical metadata. You can specify
   and override variables at the site, node or the page level and access
   them in the templates.
3. Organization: The sorter, grouper and tagger plugins provide rich
   meta-data driven organizational capabilities to hyde sites.
4. Publishing: Hyde sites can be published to variety of targets including
   github pages, Amazon S3 & SFTP.

Links
-----

1. `Changelog`_
2. `Authors`_


.. _hyde: https://github.com/lakshmivyas/hyde
.. _Hyde documentation: http://hyde.github.com
.. _Hyde Documentation Source: https://github.com/hyde/docs
.. _Cloudpanic: https://github.com/tipiirai/cloudpanic
.. _Ringce: https://github.com/lakshmivyas/ringce/tree/v3.0
.. _Authors: https://github.com/hyde/hyde/blob/master/AUTHORS.rst
.. _Changelog: https://github.com/hyde/hyde/blob/master/CHANGELOG.rst
.. _Hyde starter kit: http://merlin.rebrovic.net/hyde-starter-kit/about.html
.. _merlinrebrovic: https://github.com/merlinrebrovic
.. _rfk: https://github.com/rfk
.. _PyFS library: http://packages.python.org/fs/
.. _Hyde layout for bootstrap: https://github.com/auzigog/hyde-bootstrap
.. _auzigog: https://github.com/auzigog
.. _bootstrap framework: http://twitter.github.com/bootstrap/
.. _Hyde Powered Websites: https://github.com/hyde/hyde/wiki/Hyde-Powered
