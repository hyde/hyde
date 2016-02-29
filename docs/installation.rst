============
Installation
============

Installing hyde is as simple as running the following command::

    python -m pip install hyde

However, based on your choice and use of plugins you may need to install
additional packages. The requirements for each plugin is outlined in the
corresponding :doc:`plugins` documentation.

Dependencies
============

While your mileage may vary, we consider the following to be essential for
generating a static website with Hyde. These are a part of the requirements
file, and the above command will download and install all of them as part of
Hyde.

It is also recommended that you use `virtualenv <http://virtualenv.rtfd.org>`_
to separate the Hyde environment from other python projects. Note that
installing Hyde using ``pip`` would install all of the below. However, if you’d
like finer grained control over the packages, you can install these
individually:

1. ``argparse``: argparse is required if you are on python 2.6.
2. ``commando``: commando is a wrapper on top of argparse to give better syntax
   and support for multi-command applications.
3. ``Jinja2``: While Hyde will support many more template languages in the
   future, currently only Jinja2 is wholly supported and recommended.
4. ``Markdown``: While there are plans to add support for other markups
   (textile, restructured text, asciidoc etc..,), markdown is the one thats
   currently completely supported.
5. ``Pyyaml``: Much of Hyde’s :doc:`/configuration` is done using YAML.
6. ``pygments``: For syntax highlighting.
7. ``Typogrify``: Typogrify automatically fixes and enhances the typographical
   accuracy of your content. While this is not a technical requirement for
   Hyde, it is absolutely essential to create good looking content.



The following commands can be used to install the dependencies for Hyde
individually::

    python -m pip install argparse
    python -m pip install commando
    python -m pip install jinja2
    python -m pip install markdown
    python -m pip install pyyaml
    python -m pip install pygments
    python -m pip install smartypants
    python -m pip install typogrify
