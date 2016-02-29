====
Hyde
====

Overview
========

Hyde is a static website generator written in Python. While Hyde took life as
`Jekyll <https://jekyllrb.com/>`_'s evil twin, it has since been completely
consumed by `the dark side <https://www.python.org/>`_ and has taken on an
`identity of its own <https://groups.google.com/forum/#!forum/hyde-dev>`_.

Hyde desires to fulfill the lofty goal of removing the pain points involved in
creating and maintaining static websites.


Spotlight
=========

- Support for powerful template languages like `Jinja2
  <http://jinja.pocoo.org>`_ complemented with custom tags and filters.
- Rich :ref:`object model <object-model>` and overridable hierarchical
  :doc:`metadata </configuration>` available for use in templates.
- Configurable sorting, tagging, and grouping support.
- Extensible :doc:`plugins` architecture with text preprocessing and HTML
  postprocessing support for complex content transformations.
- Instant preview using built-in :doc:`webserver <server>` that regenerates
  content if needed.


Installation
============

Hyde is available on `PyPI <https://pypi.python.org/pypi/hyde>`_.

Installing hyde is as simple as running the following command::

    $ python -m pip install hyde


Quickstart
==========

After installing ``hyde``, creating and generating a website is extremely
simple.

To create a new Hyde website::

    $ hyde -s /path/to/your/site create

To generate the HTML::

    $ cd /path/to/your/site
    $ hyde gen

To serve the generated content, use Hyde's built-in web server::

    $ hyde serve

The website is now accessible at `http://localhost:8080
<http://localhost:8080>`_.

The webserver regenerates the necessary files to serve your request. So, you
can make your changes and simply refresh your browser to view them.

For all the supported options, read the :doc:`cli` documentation or run::

    $ hyde --help


Your First Hyde Website
=======================

Hyde uses the ``basic`` layout to generate your website by default. When you
view your generated website, you will see the following dummy pages:

#FIXME: images

You can now continue to edit the content, layout and styles to customize it to
your needs. Please see the :doc:`templates` documentation for more information.


Source
======

Hyde is `socially coded <https://github.com/hyde/hyde>`_. Feel free to fork.

Contents:

.. toctree::
    :maxdepth: 1

    installation
    cli
    configuration
    plugins
    server
    templates
    changelog


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

