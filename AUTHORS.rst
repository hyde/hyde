Hyde is developed and maintained by `Lakshmi Vyasarajan`_. The new
version of Hyde is sponsored by `Flowplayer`_ and `Tero Piirainen`_.

This version would not exist without the contributions from the
`original hyde project`_.

Contributors
======================================================================
-   |shym|_

    *   Fix various typos in documentation and code. (Issue #227)

-   |maethor|_

    *   Make username optional in SSH publisher. (Issue #222)

-   |webmaster128|_

    *   Bugfix: Add spaces to menu in ``starter`` layout. (Issue #219)

-   |QuLogic|_

    *   Refactor: Plugins reorganized by function. (Issue #170)
    *   Add HG Dates Plugin. (Issue #177)
    *   Add Clever CSS Plugin. (Issue #178)
    *   Add Sassy CSS Plugin. (Issue #179)


-   |sirlantis|_

    *   Add support for custom jinja filters. (Issue #159)


-   |ilkerde|_

    *   Add Require JS plugin. (Issue #201)


-   |jakevdp|_

    *   Add SSH publisher (Issue #205)


-   |herrlehmann|_

    *   Bugfix: Fix date time comparison in git plugin.
        (Issue#142, #199, #137)


-   |rephorm|_

    *   Add thumbnail plugin. (Issue #169, #89)


-   |jabapyth|_

    *   Add extension support for restructured text. (Issue #206)


-   |tarajane|_

    *   Bugfix: Update the .clear styleName to be .clearfix instead.
        Base.j2 applies the 'clearfix' class to the 'banner' element, and
        not the 'clear' class. (Issue #156)


-   |pib|_

    *   Bugfix: Use `_transform` instead of `transform` in Expando.
        (Issue #152, #153)


-   |adube|_

    *   Bugfix: Fix atom.j2 to use `relative_path` instead of `url` when
        referencing templates. (Issue #155, Issue#203)


-   |davefowler|_

    *   Bugfix: Infinate recursion error with resource dependencies.
        (Issue #155, Issue#200)


-   |irrelative|_

    *   Bugfix: Avoid index error if there aren't pages when iterating
        for paginator. (Issue #190)


-   |joshgerdes|_

    *   Made urlencoding safe character list configurable. (Issue #150)



-   |ErkanYilmaz|_

    *   Fixed typos in README.


-   |idank|_

    *   Bugfix: Tag archive generator uses subscript syntax to avoid failure
        when tags contain '-' or space.
    *   Bugfix: Use `check_output` to avoid a traceback when subprocess
        command fails.


-   |jd|_

    *   Bugfix: Metadata Plugin: Do not try to read meta data on
        `simple_copy` files.
    *   Bugfix: Force escape on title in Atom feed. (Issue #176)
    *   Add `node.rwalk` method for traversing the node in reverse. (Issue #176)


-   |vinilios|_

    *   Added a helper method in Expando class to ease up non existing keys
        handling.
    *   Some improvements in LessCSSPlugin to be able to build complex less
        projects (such as twitter bootstrap)


-   |nud|_

    *   Bugfix: Fix class name of `test_stylus`
    *   `$PATH` based executable discovery for `CLTransformer` plugins.
    *   Bugfix: Fix date time comparison in git plugin. (Issue#142, #199, #137)


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

    *   Bugfix: Better mime type support in hyde server
    *   Bugfix: Support empty extension in tagger archives


-   |gfuchedzhy|_

    *   Bugfix: Hyde server now takes the url cleaner plugin into account.
    *   Bugfix: Sorter excludes items that do not have sorting attributes.
    *   Bugfix: CLTransformer now gracefully handles arguments that have "=".
    *   Bugfix: All occurrences of `str` replaced with `unicode`.
    *   Bugfix: Support for encoded urls.
    *   Bugfix: Converted `content_url` and `media_url` to encoded urls
    *   Bugfix: Retain permissions in text files during generation
    *   Bugfix: Textlinks plugin: do nothing if resource doesn't use template
    *   Add thumbnail plugin. (Issue #169, #89)
    *   Bugfix: Serve files without a resource. (Issue #92)


-   |merlinrebrovic|_

    *   Hyde starter kit creation and maintenance.

-   |vincentbernat|_

    *   Bugfix: Made sorting tests more predictable
    *   Bugfix: Added more standard paths for executables
    *   Added Combine files plugin
    *   Added ignore option in site configuration to igore based on wildcards
    *   Added silent, compress and optimization parameter support for less
        css plugin
    *   Fixed plugin chaining issues
    *   Added Language(translation) plugin
    *   Added support for parameters with `=` to `CLTransformer`
    *   Added JPEGOptim plugin
    *   Bugfix: Ensure image sizer plugin handles external urls properly.
    *   Support for `output_format` configuration in markdown
    *   Add Coffeescript plugin. (Issue #172)
    *   Add thumbnail plugin. (Issue #169, #89)
    *   Add jpegtran plugin. (Issue #171)


-   |pestaa|_

    *   Added support for `UTF8` keys in `metadata` and `config`


-   |rfk|_

    *   Bugfix: LessCSSPlugin: return original text if not a .less file
    *   Added 'use_figure' configuration option for syntax tag
    *   PyFS publisher with `mtime` and `etags` support
    *   Added PyPI publisher
    *   Bugfix: Made `site.full_url` ignore fully qualified paths
    *   Added Sphinx Plugin
    *   Bugfix: PyFS publisher now checks if the pyfs module is installed.


-   |tinnet|_

    *   Bugfixes (Default template, `Syntax` template tag)



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
.. |ErkanYilmaz| replace:: Erkan Yilmaz
.. _ErkanYilmaz: https://github.com/Erkan-Yilmaz
.. |joshgerdes| replace:: Josh Gerdes
.. _joshgerdes: https://github.com/joshgerdes
.. |irrelative| replace:: irrelative
.. _irrelative: https://github.com/irrelative
.. |davefowler| replace:: Dave Fowler
.. _davefowler: https://github.com/davefowler
.. |adube| replace:: Alexandre Dubé
.. _adube: https://github.com/adube
.. |pib| replace:: Paul Bonser
.. _pib: https://github.com/pib
.. |tarajane| replace:: Tara Feener
.. _tarajane: https://github.com/tarajane
.. |jabapyth| replace:: Jared Forsyth
.. _jabapyth: https://github.com/jabapyth
.. |rephorm| replace:: Brian Mattern
.. _rephorm: https://github.com/rephorm
.. |herrlehmann| replace:: herr-lehmann
.. _herrlehmann: https://github.com/herr-lehmann
.. |jakevdp| replace:: Jake Vanderplas
.. _jakevdp: https://github.com/jakevdp
.. |ilkerde| replace:: ilkerde
.. _ilkerde: https://github.com/ilkerde
.. |sirlantis| replace:: Marcel Jackwerth
.. _sirlantis: https://github.com/sirlantis
.. |QuLogic| replace:: Elliott Sales de Andrade
.. _QuLogic: https://github.com/QuLogic
.. |webmaster128| replace:: Simon Warta
.. _webmaster128: https://github.com/webmaster128
.. |maethor| replace:: Guillaume Subiron
.. _maethor: https://github.com/maethor
.. |shym| replace:: shym
.. _shym: https://github.com/shym
