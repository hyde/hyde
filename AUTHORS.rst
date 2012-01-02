Hyde is developed and maintained by `Lakshmi Vyasarajan`_. The new version of
Hyde is sponsored by `Flowplayer`_ and `Tero Piirainen`_.

This version would not exist without the contributions from the
`original hyde project`_.

Contributors
===============================================================================
-   |idank|_

    *   Bug Fix: Tag archive generator uses subscript syntax to avoid failure when tags contain '-' or space.
    *   Bug Fix: Use `check_output` to avoid a traceback when subprocess command fails.

-   |jd|_

    *   Bug Fix: Metadata Plugin: Do not try to read meta data on `simple_copy` files.

    |vinilios|_

    *   Added a helper method in Expando class to ease up non existing keys handling.
    *   Some improvements in LessCSSPlugin to be able to build complex less projects (such as twitter bootstrap)

-   |nud|_

    *   Bug Fix: Fix class name of `test_stylus`
    *   `$PATH` based executable discovery for `CLTransformer` plugins.

-   |theevocater|_

    *   Fixed Authors link in README

-   |tcheneau|_

    *   Added support for AsciiDoc.

-   |gr3dman|_

    *   Added paginator plugin and tests

-   |benallard|_

    *   Added restructuredText plugin
    *   Added restructuredText filter
    *   Added traceback support for errors when server is running

-   |stiell|_

    *   Bug Fix: Better mime type support in hyde server
    *   Bug Fix: Support empty extension in tagger archives

-   |gfuchedzhy|_

    *   Bug Fix: Hyde server now takes the url cleaner plugin into account.
    *   Bug Fix: Sorter excludes items that do not have sorting attributes.
    *   Bug Fix: CLTransformer now gracefully handles arguments that have "=".
    *   Bug Fix: All occurrences of `str` replaced with `unicode`.
    *   Bug Fix: Support for encoded urls.
    *   Bug Fix: Converted `content_url` and `media_url` to encoded urls
    *   Bug Fix: Retain permissions in text files during generation
    *   Bug Fix: Textlinks plugin: do nothing if resource doesn't use template

-   |merlinrebrovic|_

    *   Hyde starter kit

-   |vincentbernat|_

    *   Bug Fix: Made sorting tests more predictable
    *   Bug Fix: Added more standard paths for executables
    *   Added Combine files plugin
    *   Added ignore option in site configuration to igore based on wildcards
    *   Added silent, compress and optimization parameter support for less css plugin
    *   Fixed plugin chaining issues
    *   Added Language(translation) plugin
    *   Added support for parameters with `=` to `CLTransformer`
    *   Added JPEGOptim plugin
    *   Bug Fix: Ensure image sizer plugin handles external urls properly.
    *   Support for `output_format` configuration in markdown

-   |pestaa|_

    *   Added support for `UTF8` keys in `metadata` and `config`

-   |rfk|_

    *   Bug fix: LessCSSPlugin: return original text if not a .less file
    *   Added 'use_figure' configuration option for syntax tag
    *   PyFS publisher with `mtime` and `etags` support
    *   Added PyPI publisher
    *   Bug fix: Made `site.full_url` ignore fully qualified paths
    *   Added Sphinx Plugin
    *   Bug fix: PyFS publisher now checks if the pyfs module is installed.

-   |tinnet|_

    *   Bug fixes (Default template, `Syntax` template tag)


.. _Lakshmi Vyasarajan: http://twitter.com/lakshmivyas
.. _Flowplayer: http://flowplayer.org
.. _Tero Piirainen: http://cloudpanic.com
.. _original hyde project: https://github.com/lakshmivyas/hyde
.. |rfk| replace:: Ryan Kelly
.. _rfk: https://github.com/rfk
.. |tinnet| replace:: Tinnet Coronam
.. _tinnet: https://github.com/tinnet
.. |pestaa| replace:: pestaa
.. _pestaa: https://github.com/pestaa
.. |vincentbernat| replace:: Vincent Bernat
.. _vincentbernat: https://github.com/vincentbernat
.. |merlinrebrovic| replace:: Merlin Rebrović
.. _merlinrebrovic: https://github.com/merlinrebrovic
.. |gfuchedzhy| replace:: Grygoriy Fuchedzhy
.. _gfuchedzhy: https://github.com/gfuchedzhy
.. |stiell| replace:: Stian Ellingsen
.. _stiell: https://github.com/stiell
.. |benallard| replace:: Benoît Allard
.. _benallard: https://github.com/benallard
.. |gr3dman| replace:: Gareth Redman
.. _gr3dman: https://github.com/gr3dman
.. |tcheneau| replace:: Tony Cheneau
.. _tcheneau: https://github.com/tcheneau
.. |theevocater| replace:: Jacob Kaufman
.. _theevocater: https://github.com/theevocater
.. |nud| replace:: Steve Frécinaux
.. _nud: https://github.com/nud
.. |vinilios| replace:: Kostas Papadimitriou
.. _vinilios: https://github.com/vinilios
.. |jd| replace:: Julien Danjou
.. _jd: https://github.com/jd
.. |idank| replace:: idank
.. _idank: https://github.com/idank