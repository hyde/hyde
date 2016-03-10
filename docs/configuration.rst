=============
Configuration
=============

Hyde is configured using one or more ``yaml`` files. On top of all the niceties
``yaml`` provides out of the box, Hyde also adds a few power features to manage
complex websites.

If a site has a ``site.yaml`` file in the root directory, it is used as the
configuration for generating the website. This can be overridden by providing a
command line option. See the `command line reference <CLI>`_ for details.


Inheritance
===========

Configuration files can inherit from another file using the ``extends`` option.
For example, the following configuration will inherit all properties from
``site.yaml`` and override the ``mode`` property::

    extends: site.yaml
    mode: production

This is useful for customizing the site to operate in different modes. For
example, when running locally you may want your media files to come from
``/media`` but on production you may have a subdomain and want the media to
come from ``http://abc.example.com/media``.

This can be accomplished by creating an ``extended`` configuration file and
overriding the ``media_url`` property.

.. todo:: Add link to real example config.


The following settings can be defined for use in templates:

Paths & URLs
============

+----------------+-----------------------------------------------------------+
| ``media_root`` | The root path where media files (images, CSS, JavaScript, |
|                | etc.) can be found. This may be used by plugins for       |
|                | special processing. If your website does not have a       |
|                | folder that contains all media, you can safely omit this  |
|                | property. Defaults to ``media``.                          |
+----------------+-----------------------------------------------------------+
| ``media_url``  | The url prefix for serving media files. If you are using  |
|                | a CDN like Amazon S3 or the Rackspace cloud and host all  |
|                | of your media files from there, you can make use of this  |
|                | property to specify the prefix for all media files.       |
|                | Defaults to ``/media``.                                   |
+----------------+-----------------------------------------------------------+
| ``base_url``   | The base url from which the site is served. If you are    |
|                | hosting the website in a subdomain or as part of a larger |
|                | website, you can specify this property to indicate the    |
|                | path of this project in your website. Defaults to ``/``.  |
+----------------+-----------------------------------------------------------+


Plugins and Templates
=====================

+--------------+--------------------------------------------------------------+
| ``template`` | The template engine to use for processing the website can be |
|              | specified in the configuration file as a Python class path.  |
|              | Currently, only ``Jinja2`` is supported. Reserved for future |
|              | use. Defaults to                                             |
|              | ``hyde.ext.templates.jinja.jinja2template``.                 |
+--------------+--------------------------------------------------------------+
| ``plugins``  | Plugins are specified as list of Python class paths. Events  |
|              | that are raised during the generation of the website are     |
|              | issued to the plugins in the same order as they are listed   |
|              | here. You can learn more about how the individual plugins    |
|              | are configured in the `plugin documentation <plugins>`_.     |
|              | Optional. By default, no plugins are enabled.                |
+--------------+--------------------------------------------------------------+

.. _object-model:

Context Data
============

The context section contains key / value pairs that are simply passed on to the
templates.

For example, given the following configuration, the statement
``{{ app.current_version }}`` in any template will output ``0.6``::

    context:
        data:
            app:
                version: 0.6

By default, no context variables are provided.


Context Data Providers
======================

Providers are special constructs used to import data into the context. For
example, data from a database can be exported as ``yaml`` and imported as a
provider. For example, the following snippets would import the data in
``app-versions.yaml`` into ``context[versions]``. This data can then be used
directly in templates in this manner: ``{{ versions.latest }}``.

.. TODO: Investigate code-block captions here. This feature was added in sphinx
   1.3, but doc8 seems to not support that yet.

.. code::

    # site.yaml
    context:
        providers:
            versions: app-versions.yaml


.. code::

    # app-versions.yaml
    latest: 0.6


Markdown
========

Extensions and extension configuration for markdown can be configured in the
``markdown`` property. You can read about markdown extensions in the
`Python-Markdown documentation <https://pythonhosted.org/Markdown/>`_.

The following configuration will use the ``def_list``, ``tables``, ``headerid``
extensions in Python-Markdown.
