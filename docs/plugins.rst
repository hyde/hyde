=======
Plugins
=======

Hyde is built with a nuclear engine that is stripped down but powerful. Even
core features like ``metadata`` are added as plugins to keep the engine bloat
free.

Hyde’s plugin architecture is event driven; plugins get notified during the
course of the generation to allow them to alter/guide the generation process.

If you are interested in creating plugins for Hyde, you can read the developer
documentation.

Configuration
=============

Hyde’s plugins get loaded if they are listed in the plugins section of
:doc:`configuration`. Plugins also accept additional parameters in their
respective sections. For example, ``MyAwesomePlugin`` will get parameters from
``myawesome`` section in the configuration file.

In the box
==========

Hyde is shipped with the following plugins:


Metadata
========

Metadata
--------
.. autoclass:: hyde.ext.plugins.meta.MetaPlugin

AutoExtend
----------
.. autoclass:: hyde.ext.plugins.meta.AutoExtendPlugin

Sorter
------
.. autoclass:: hyde.ext.plugins.meta.SorterPlugin


CSS
===

Less CSS
--------
.. autoclass:: hyde.ext.plugins.css.LessCSSPlugin


Text Replacement
================

Blockdown
---------
.. autoclass:: hyde.ext.plugins.text.BlockdownPlugin

Mark
----
.. autoclass:: hyde.ext.plugins.text.MarkingsPlugin

Refer
-----
.. autoclass:: hyde.ext.plugins.text.ReferencePlugin

Textlinks
---------
.. autoclass:: hyde.ext.plugins.text.TextlinksPlugin

Syntext
-------
.. autoclass:: hyde.ext.plugins.text.SyntextPlugin


Structure
=========

Folder Flattener
----------------
.. autoclass:: hyde.ext.plugins.structure.FlattenerPlugin
