Version 0.9.0

.. image:: https://travis-ci.org/hyde/hyde.svg?branch=master

Overview
========

Hyde is a static site generator written in python.

Currently hyde is only supported on python 2.7.x.  Python 3.x support is being
tackled in version 1.0, thanks to `llonchj`_, `jonafato`_ and `descent098`_ for their work in
moving towards 1.0. If you are interested in seeing the progress towards the 1.0 release check the current `roadmap`_

A new slack has been created for current development, any information about
how to help or contribute to active development can be found there:

`<https://join.slack.com/t/hyde-network/shared_invite/zt-cxbso1ba-pHM1BGbDA9t9dBa20hLVNQ>`_

Features
--------

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

Installation
------------

To get the latest released version:

::

    pip install hyde

To install directly from source:

::

    pip install git+https://github.com/hyde/hyde.git

Getting Started
---------------


Creating a new hyde project
---------------------------

Enter the following command to create the initial project files using the *test* layout. In this case it will create a new folder called *test_site* and fill it with what you need to get started.:

::

        hyde -s test_site create


Next we will use ``hyde gen`` to generate our static site:

::

        cd test_site
        hyde gen
        
This will create a folder called *deploy* that will have our generated static site in it.

Additional Starter Resources
----------------------------

Here are a few additional resources you can take a look at for the initial build of your site.

`Hyde starter kit`_ by `merlinrebrovic`_ is a really nice way to get started
with hyde.

`Hyde layout for bootstrap`_ by `auzigog`_ is also a good alternative if you
like Twitter's `bootstrap framework`_.

You can also take a look at `Hyde Powered Websites`_ for inspiration and
reference.


Previewing the website
----------------------

Now that the site has been generated we can see what it will look like by running the ``serve`` command in the root directory of the project:

::

        hyde serve

Now open up localhost:8080 in a browser and voila you can preview your site.

Publishing the website
----------------------

Once you are ready to publish the website simply go into the root directory of the project and run the following command (in this case to publish to github):

::

        hyde publish -p github


Hyde supports extensible publishers that have baked in support by modifying the ``site.yaml`` file in your project root directory.

Github
~~~~~~~

The hyde documentation is published to github pages using this command with
the following configuration:

``site.yaml``

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

1. `julien.danjou.info`_
2. `luffy.cx`_
3. `Cloudpanic`_(source only, site is no longer online)
4. `Hyde Documentation Source`_


Links
-----

1. `Changelog`_
2. `Authors`_


.. _hyde: https://github.com/lakshmivyas/hyde
.. _Hyde documentation: http://hyde.github.com
.. _Hyde Documentation Source: https://github.com/hyde/docs
.. _Cloudpanic: https://github.com/tipiirai/cloudpanic
.. _Authors: https://github.com/hyde/hyde/graphs/contributors
.. _Changelog: https://github.com/hyde/hyde/blob/master/CHANGELOG.rst
.. _Hyde starter kit: http://merlin.rebrovic.net/hyde-starter-kit/about.html
.. _merlinrebrovic: https://github.com/merlinrebrovic
.. _rfk: https://github.com/rfk
.. _PyFS library: http://packages.python.org/fs/
.. _Hyde layout for bootstrap: https://github.com/auzigog/hyde-bootstrap
.. _auzigog: https://github.com/auzigog
.. _bootstrap framework: http://twitter.github.com/bootstrap/
.. _Hyde Powered Websites: https://github.com/hyde/hyde/wiki/Hyde-Powered
.. _hyde-dev: https://groups.google.com/forum/#!forum/hyde-dev
.. _julien.danjou.info: https://github.com/jd/julien.danjou.info
.. _luffy.cx: https://github.com/vincentbernat/www.luffy.cx
.. _jonafato: https://github.com/jonafato
.. _llonchj: https://github.com/llonchj
.. _descent098: https://github.com/Descent098
.. _roadmap: https://github.com/hyde/hyde/projects/1
