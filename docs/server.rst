==========
Web Server
==========

The Hyde web server is a simple, bare-bones webserver based on Python's `Simple
HTTP Request Handler <http://docs.python.org/library/simplehttpserver.html>`_.

The following command starts the built in webserver::

    hyde serve

You can now access your website at ``http://localhost:8080``.

The webserver regenerates the necessary files to serve your request. So, you
can make your changes and simply refresh your browser to view them.


Special Parameters
==================

The Hyde webserver supports just one special parameter: ``refresh``.

If you add ``?refresh`` to the URL, the server regenerates the site completely
and refreshes your browser. Note that for larger sites, this may take a few
seconds to complete.


Dependencies
============

Information about dependencies between pages are stored in your site root
directory in the ``.hyde_deps`` file. If regeneration is not consistent with
your expectations, you can simply delete this file, and Hyde will build the
dependency tree again.
