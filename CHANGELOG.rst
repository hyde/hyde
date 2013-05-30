Version 0.8.7 (2013-05-30)
============================================================

*   Bugfix: Ensure dependencies are handled properly when using the
    combine plugin. (Issue #120).
*   Bugfix: Ensure external urls are encoded properly. (Issue #158).

    -   **BREAKING**:  While this change will correct the weird encoding
        behavior, this also changes the way ``xxx_url`` macros work.
    -   Do not encode the url bases (``base_url``, ``media_url``). Only
        the path component needs to be encoded.

*   Bugfix: Fix subfolders for root paths on windows. (Issue #167).

    -   Ensure that subfolders for ``layout_root``, ``content_root``,
        ``media_root`` and ``deploy_root`` works reliably
        on windows. Use ``fully_expanded_path`` for all path components.

*   Bugfix: Context providers now accept all valid yaml data (Issue #189).
*   Bugfix: Fixed ``raise_exceptions`` command line parameter handling.
*   Better exception handling. (Issue #204)

    -   Hyde now propagates exceptions
    -   Hyde does not raise exceptions by default. ``-x`` flag is required
        for raising exceptions on error.
    -   Traceback is available in the ``verbose`` mode

*   Upgraded to commando 0.3.4
*   Upgraded to Jinja 2.7
*   Make sorter's prev/next links circular. (Issue #208)
*   Bugfix: Include project artifacts in sdist. (Issue #211)

    -   Add LICENSE, AUTHORS and CHANGELOG to MANIFEST.in

*   Add "Hyde contributors" to LICENSE copyright.
*   Upgrade ``UglifyPlugin`` to use 2.3.5 version of uglify. (Issue #214)
*   Add support for draft blog posts. (Issue #213)
*   Bugfix: Use ``clearfix`` class in ``listing.j2``. (Issue #156)
*   Bugfix: Use ``relative_path`` instead of url in ``macros.j2``. (Issue #180)


Version 0.8.6 (2013-04-30)
============================================================

Thanks to @QuLogic:

*   Refactor: Plugins reorganized by function. (Issue #170)
*   Add HG Dates Plugin. (Issue #177)
*   Add Clever CSS Plugin. (Issue #178)
*   Add Sassy CSS Plugin. (Issue #179)

Thanks to @sirlantis:

*   Add support for custom jinja filters. (Issue #159)

Thanks to @gfuchedzhy

*   Bugfix: Serve files without a resource. (Issue #92)

Thanks to @ilkerde:

*   Add Require JS plugin. (Issue #201)

Thanks to @jakevdp:

*   Add SSH publisher. (Issue #205)

Thanks to @herr-lehmann and @nud:

*   Bugfix: Fix date time comparison in git plugin. (Issue#142, #199, #137)

Thanks to @rephorm, @gfuchedzhy and @vincentbernat:

*   Add thumbnail plugin. (Issue #169, #89)

Thanks to @vincentbernat:

*   Add Coffeescript plugin. (Issue #172)
*   Add jpegtran plugin. (Issue #171)

Thanks to @jabapyth:

*   Add extension support for restructured text. (Issue #206)

Thanks to @tarajane:

*   Bugfix: Update the .clear styleName to be .clearfix instead.
    Base.j2 applies the 'clearfix' class to the 'banner' element, and not
    the 'clear' class. (Issue #156)

Thanks to @pib:

*   Bugfix: Use ``_transform`` instead of ``transform`` in Expando.
    (Issue #152, #153)

Version 0.8.5 (2013-04-17)
============================================================

*   Upgrade dependencies and setup for 0.8.5
*   Remove ``hyde.fs`` use ``fswrap`` package instead.
*   Remove logging functions from ``hyde.util``. Use ``commando.util`` instead.
*   Remove ``hyde.loader``. Use ``commando.util.load_python_object`` instead.
*   Bugfix: Use the released version of typogrify. (Issue #193)
*   Bugfix: Fixed stylus ``indent`` issues with empty files. (Issue #161)
*   Bugfix: Added support for plugin paths relative to site. (Issue #107)
*   Bugfix: Folder Flattener updates node's ``relative_deploy_path`` & ``url``
    attributes as well. (Issue #126)
*   BREAKING: As part of the above fix, ``resource.url`` is
    prefixed with a ``/``. (Issue #126)
*   Added ``simple_copy`` feature to account for unprocessable files that
    are nonetheless required to be deployed (Issue #121)
*   Bugfix: Relative path was used in the server as the sitepath (Issue #119)
*   Plugins now support inclusion filters. (Issue #112)

    -   ``include_file_patterns`` property accepts globs to filter by file name.
    -   ``include_paths`` accepts paths relative to content.
    -   ``begin_node`` and ``node_complete`` honor ``include_paths``
    -   ``begin_text_resource``, ``text_resource_complete``,
        ``begin_binary_resource`` and ``binary_resource_complete`` honor both.

*   Bugfix: Unsorted combine files fixed. (Issue #111)
*   Added an optional sorting parameter. (Issue #111)
*   Bugfix:  Modified combine plugin to process during
    ``begin_text_resource``. (Issue #110)
*   Modified combine plugin to support relative paths and recursion.
    (Issue #108)
*   Added ability to specify safe characters in ``content_url``,
    ``media_url`` functions and ``urlencode`` filter. (Issue #103)

Thanks to @idank

*   Bugfix: Use ``check_output`` to avoid a traceback when subprocess
    command fails.
*   Bugfix: Tag archive generator uses subscript syntax to avoid failure
    when tags contain '-' or space. (Issue #130)

Thanks to @jd

*   Bugfix: Metadata Plugin: Do not try to read meta data on ``simple_copy``
    files. (Issue #124, Issue #121)
*   Bugfix: Force escape on title in Atom feed. (Issue #176)
*   Add ``node.rwalk`` method for traversing the node in reverse. (Issue #176)

Thanks to @vinilios

*   Added a helper method in Expando class to ease up non existing keys
    handling. (Issue #117)
*   Some improvements in LessCSSPlugin to be able to build complex less
    projects (such as twitter bootstrap) (Issue #117)

Thanks to @Erkan-Yilmaz

*   Fixed typos in README.

Thanks to @merlinrebrovic

*   Updates and improvements to the starter template.

    * Cleans up CSS.
    * Handles page title endings more elegantly.
    * Renders the advanced menu below the basic one.
    * Corrects and updates content.
    * Explains how to generate and serve the template.
    * Makes it more straightforward to contribute.

Thanks to @joshgerdes:

*   Made urlencoding safe character list configurable. (Issue #150)

Thanks to @irrelative:

*   Bugfix: Avoid index error if there aren't pages when iterating
    for paginator. (Issue #190)

Thanks to @davefowler:

*   Bugfix: Infinate recursion error with resource dependencies.
    (Issue #155, Issue#200)

Thanks to @adube:

*   Bugfix: Fix atom.j2 to use ``relative_path`` instead of ``url`` when
    referencing templates. (Issue #155, Issue#203)


Version 0.8.4 (2011-11-09)
============================================================

*   Bugfix: Configuration now gets reloaded when server regenerates (Issue #70)
*   Bugfix: Added styles for codebox (Issue #69)
*   Tagger now generates archives upfront in begin_site (Issue #72)
*   **Breaking**: The default nodemeta file has been changed to meta.yaml
*   Added test for codehilite markdown extension (Issue #82)
*   Added rst_directive.py from the pygments repository (Issue #82)
*   Added support for ignoring nodes (Issue #80)
*   Hyde now ignores .hg, .svn and .git by default (Issue #80)
*   Added support for default publisher (Issue #83)
*   Added ``urlencode`` and ``urldecode`` filters. (Issue #102)
*   Bugfix: Fixed tests for Issue #88
*   Added tests for sorting groups
*   Added support for loading modules from the site path. Thanks to
    @theomega for the idea (Issue #78 & #79)
*   Added docutils to dev-req.txt
*   Bugfix: Fixed uglify-js tests

Thanks to @nud

*   ``$PATH`` based executable discovery for ``CLTransformer`` plugins.
    (Issue #100)
*   Bugfix: Fix class name of ``test_stylus`` (Issue #97)

Thanks to @gfuchedzhy

*   Bugfix: Textlinks plugin: do nothing if resource doesn't use template.
    (Issue #96)
*   Bugfix: Retain permissions in text files during generation (Issue #90)
*   Bugfix: Added support for encoded urls to hyde server. (Issue #88)
*   Bugfix: Converted ``content_url`` and ``media_url`` to encoded urls.
    (Issue #88)
*   Bugfix: All occurrences of ``str`` replaced with ``unicode``.
    (Issue #87)
*   Bugfix: CLTransformer now gracefully handles arguments that have "=".
    (Issue #58)

Thanks to @vincentbernat

*   Support for ``output_format`` configuration in markdown (Issue #89)

Thanks to @merlinrebrovic

*   Hyde starter kit extended with advanced options (Issue #68)

Thanks to @tcheneau

*   Added support for AsciiDoc. (Issue #76)

Thanks to @gr3dman

*   Added paginator plugin and tests (Issue #73)

Thanks to @benallard

*   Added restructuredText plugin (Issue #63)
*   Added restructuredText filter (Issue #63)
*   Added traceback support for errors when server is running (Issue #63)

Thanks to @rfk

*   Added Sphinx Plugin (Issue #62)
*   Bugfix: PyFS publisher now checks if the pyfs module is installed.
    (Issue #62)

Version 0.8.3 (2011-06-20)
============================================================

*   Bugfix: A bad bug in Expando that modified the ``__dict__`` has been fixed.
    (Issue #53)
*   Tags now support metadata. Metadata can be provided as part of the tagger
    plugin configuration in ``site.yaml``
*   Ensured that the context data & providers behave in the same manner. Both
    get loaded as expandos. (Issue #29)
*   ``hyde serve`` now picks up changes in config data automatically.
    (Issue #24)
*   Bugfix: ``hyde create`` only fails when ``content``, ``layout`` or
    ``site.yaml`` is present in the target directory. (Issue #21)
*   Bugfix: Exceptions are now handled with ``ArgumentParser.error``.
*   Bugfix: Sorter excludes items that do not have sorting attributes.
    (Issue #18)
*   Wrapped ``<figure>`` inside ``<div>`` to appease markdown. (Issue #17)
*   Added ``display:block`` for html5 elements in basic template so that it
    works in not so modern browsers as well. (Issue #17)

Thanks to Joe Steeve.

*   Changed deploy location for main.py and fixed entry point in
    ``setup.py``. (Issue #56)

Thanks to @stiell

*   Bugfix: Better mime type support in hyde server (Issue #50)
*   Bugfix: Support empty extension in tagger archives (Issue #50)

Thanks to @gfuchedzhy

*   Bugfix: Hyde server now takes the url cleaner plugin into account.
    (Issue #54)

Thanks to @vincentbernat

*   Bugfix: Ensure image sizer plugin handles external urls properly.
    (Issue #52)

Thanks to @rfk

*   Added PyPI publisher (Issue #49)
*   Bugfix: Made ``site.full_url`` ignore fully qualified paths (Issue #49)

Thanks to @vincentbernat

*   Added JPEG Optim plugin (Issue #47)
*   Fixes to CLTransformer (Issue #47)

Version 0.8.2 (2011-05-10)
============================================================

Thanks to @merlinrebrovic

*   Added hyde starter kit (Issue #43)

Thanks to @vincentbernat

*   Added git dates plugin (Issue #42)
*   Added Image size plugin (Issue #44)
*   Added silent, compress and optimization parameter support for less css
    plugin (Issue #40)
*   Fixed plugin chaining issues (Issue #38)
*   Added Language(translation) plugin (Issue #37)
*   Bugfix: Made sorting tests more predictable (Issue #41)
*   Bugfix: Added more standard paths for executables (Issue #41)
*   Added Combine files plugin (Issue #39)
*   Added ignore option in site configuration to igore based on wildcards
    (Issue #32)

Thanks to @pestaa

*   Added support ``UTF8`` keys in ``metadata`` and ``config`` (Issue #33)


Version 0.8.1 (2011-05-09)
============================================================

Thanks to @rfk.

*   Updated to use nose 1.0 (Issue #28)
*   Bugfix: LessCSSPlugin: return original text if not a .less file
    (Issue #28)
*   PyFS publisher with mtime and etags support. (Issue #28)

Version 0.8 (2011-04-13)
============================================================

*   Relative path bugs in windows generation have been fixed.

Version 0.8rc3 (2011-04-12)
============================================================

*   Fixed a jinja2 loader path issue that prevented site generation in windows
*   Fixed tests for stylus plugin to account for more accurate color
    manipulation in the latest stylus
