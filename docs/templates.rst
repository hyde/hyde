=========
Templates
=========

Creating Layouts
================

Hyde is designed to support more than one template language for creating
layouts, however, it currently only supports `Jinja2
<http://jinja.pocoo.org>`_. This section of the documentation will focus on
creating templates using Jinja2. If you are not familiar with Jinja2, it's a
good idea to go through the `most excellent Jinja2 documentation
<http://jinja.pocoo.org/docs/dev/templates/>`_.


Site Structure
==============

Hyde encourages separation of content from layout. The following shows a
typical structure of a Hyde website::

    ├── content/
    │   ├── about.html
    │   ├── blog/
    │   ├── index.html
    │   ├── layout/
    │   │   ├── base.j2
    │   │   └── macros.j2
    │   ├── media/
    │   │   ├── css/
    │   │   ├── images/
    │   │   └── js/
    │   ├── portfolio/
    │   └── projects/
    └── site.yml

good objective is to have all the files in content contain as little layout as
possible and be written with a text oriented markup language like `markdown
<https://daringfireball.net/projects/markdown/>`_.  While its not always
possible to achieve 100% separation, hyde provides several nice tools to get
very close to that goal.


Context Variables
=================

Hyde by default makes the following variables available for templates:

- ``site``: Represents the container object of the entire site.
- ``node``: The node (folder) where the current file resides.
- ``resource``: The resource (file) that is currently being processed.
- Context variables: all variables defined under the ``context`` section of the
  site configuration are available to the templates.

Read more information about the ``site``, ``mode``, and ``resource`` variables
in the `site model documentation <#>`_.

Read more information about context variables in the `configuration
documentation <#config>`_.
