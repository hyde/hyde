Version 0.8.1

A brand new **hyde**
====================

This is the new version of `hyde`_ under active development. Hyde
documentation is a work in progress and can be found `here`_.

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


Hyde supports extensible publishers. Right now only github is implemented.
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

Examples
--------

1. `Hyde Documentation`_
2. `Cloudpanic`_
3. `Ringce`_

A brief list of features
------------------------

1. Support for multiple templates (although only ``Jinja2`` is currently
   implemented)
2. The different processor modules in the previous version are now
   replaced by a plugin object. This allows plugins to listen to events
   that occur during different times in the lifecycle and respond
   accordingly.
3. Metadata: Hyde now supports hierarchical metadata. You can specify
   and override variables at the site, node or the page level and access
   them in the templates.
4. Organization: The sorter, grouper and tagger plugins provide rich
   meta-data driven organizational capabilities to hyde sites.
5. Syntactic Sugar: Because of the richness of the plugin
   infrastructure, hyde can now provide additional syntactic sugar to
   make the content more readable. See ``blockdown`` and ``syntext``
   plugin for examples.

Next Steps
----------

1. Documentation
2. Default Layouts ✓
3. Django Support
4. Plugins:

   -  Tags ✓
   -  Atom / RSS ✓
   -  Text Compressor (CSS, JS, HTML) ✓
   -  Image optimizer ✓

Links
-----

1. `Changelog`_
2. `Authors`_


.. _hyde: https://github.com/lakshmivyas/hyde
.. _here: http://hyde.github.com
.. _Hyde Documentation: https://github.com/hyde/docs
.. _Cloudpanic: https://github.com/tipiirai/cloudpanic
.. _Ringce: https://github.com/lakshmivyas/ringce/tree/v3.0
.. _Authors: https://github.com/hyde/hyde/blob/master/AUTHORS
.. _Changelog: https://github.com/hyde/hyde/blob/master/CHANGELOG.rst
