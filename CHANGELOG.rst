Version 0.8.5a14
============================================================

*   Bug Fix: Fixed stylus `indent` issues with empty files. (Issue #161)

Version 0.8.5a14
============================================================

*   Bug Fix: Added support for plugin paths relative to site. (Issue #107)

Version 0.8.5a13
============================================================

Thanks to @idank

*   Bug Fix: Use `check_output` to avoid a traceback when subprocess command fails.


Version 0.8.5a12
============================================================

Thanks to @idank

*   Bug Fix: Tag archive generator uses subscript syntax to avoid failure when tags contain '-' or space. (Issue #130)

Version 0.8.5a11
============================================================

*   Bug Fix: Folder Flattener updates node's `relative_deploy_path` & `url` attributes as well. (Issue #126)
*   BREAKING: As part of the above fix, `resource.url` is prefixed with a `/`. (Issue #126)

Version 0.8.5a10
============================================================

Thanks to @jd

*   Bug Fix: Metadata Plugin: Do not try to read meta data on `simple_copy` files. (Issue #124, Issue #121)

Version 0.8.5a9
============================================================

Thanks to @vinilios

*   Added a helper method in Expando class to ease up non existing keys handling. (Issue #117)
*   Some improvements in LessCSSPlugin to be able to build complex less projects (such as twitter bootstrap) (Issue #117)

Version 0.8.5a8
============================================================

*   Added `simple_copy` feature to account for unprocessable files that
    are nonetheless required to be deployed (Issue #121)

Version 0.8.5a7
============================================================
*   Bug Fix: Relative path was used in the server as the sitepath (Issue #119)

Version 0.8.5a6
============================================================

*   Plugins now support inclusion filters. (Issue #112)
    -   `include_file_patterns` property accepts globs to filter by file name.
    -   `include_paths` accepts paths relative to content.
    -   `begin_node` and `node_complete` honor `include_paths`
    -   `begin_text_resource`, `text_resource_complete`, `begin_binary_resource`
        and `binary_resource_complete` honor both.

Version 0.8.5a5
============================================================

*   Bug Fix: Unsorted combine files fixed. (Issue #111)

Version 0.8.5a4
============================================================

*   Added an optional sorting parameter. (Issue #111)

Version 0.8.5a3
============================================================

*   Bug Fix:  Modified combined plugin to process during `begin_text_resource`. (Issue #110)

Version 0.8.5a2
============================================================

*   Modified combined plugin to support relative paths and recursion. (Issue #108)

Version 0.8.5a1
============================================================

*   Added ability to specify safe characters in `content_url`,
    `media_url` functions and `urlencode` filter. (Issue #103)

Version 0.8.4
============================================================

*   Bug Fix: Configuration now gets reloaded when server regenerates (Issue #70)
*   Bug Fix: Added styles for codebox (Issue #69)
*   Tagger now generates archives upfront in begin_site (Issue #72)
*   **Breaking**: The default nodemeta file has been changed to meta.yaml
*   Added test for codehilite markdown extension (Issue #82)
*   Added rst_directive.py from the pygments repository (Issue #82)
*   Added support for ignoring nodes (Issue #80)
*   Hyde now ignores .hg, .svn and .git by default (Issue #80)
*   Added support for default publisher (Issue #83)
*   Added `urlencode` and `urldecode` filters. (Issue #102)
*   Bug Fix: Fixed tests for Issue #88
*   Added tests for sorting groups
*   Added support for loading modules from the site path. Thanks to
    @theomega for the idea (Issue #78 & #79)
*   Added docutils to dev-req.txt
*   Bug Fix: Fixed uglify-js tests

Thanks to @nud

*   `$PATH` based executable discovery for `CLTransformer` plugins. (Issue #100)
*   Bug Fix: Fix class name of `test_stylus` (Issue #97)

Thanks to @gfuchedzhy

*   Bug Fix: Textlinks plugin: do nothing if resource doesn't use template (Issue #96)
*   Bug Fix: Retain permissions in text files during generation (Issue #90)
*   Bug Fix: Added support for encoded urls to hyde server. (Issue #88)
*   Bug Fix: Converted `content_url` and `media_url` to encoded urls. (Issue #88)
*   Bug Fix: All occurrences of `str` replaced with `unicode`. (Issue #87)
*   Bug Fix: CLTransformer now gracefully handles arguments that have "=". (Issue #58)

Thanks to @vincentbernat

*   Support for `output_format` configuration in markdown (Issue #89)

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
*   Bug fix: PyFS publisher now checks if the pyfs module is installed. (Issue #62)

Version 0.8.3
============================================================

*   Bug Fix: A bad bug in Expando that modified the `__dict__` has been fixed.
    (Issue #53)
*   Tags now support metadata. Metadata can be provided as part of the tagger
    plugin configuration in `site.yaml`
*   Ensured that the context data & providers behave in the same manner. Both
    get loaded as expandos. (Issue #29)
*   `hyde serve` now picks up changes in config data automatically.
    (Issue #24)
*   Bug Fix: `hyde create` only fails when `content`, `layout` or `site.yaml`
    is present in the target directory. (Issue #21)
*   Bug Fix: Exceptions are now handled with `ArgumentParser.error`.
*   Bug Fix: Sorter excludes items that do not have sorting attributes.
    (Issue #18)
*   Wrapped `<figure>` inside `<div>` to appease markdown. (Issue #17)
*   Added `display:block` for html5 elements in basic template so that it
    works in not so modern browsers as well. (Issue #17)

Thanks to Joe Steeve.

*   Changed deploy location for main.py and fixed entry point in
    `setup.py`. (Issue #56)

Thanks to @stiell

*   Bug Fix: Better mime type support in hyde server (Issue #50)
*   Bug Fix: Support empty extension in tagger archives (Issue #50)

Thanks to @gfuchedzhy

*   Bug Fix: Hyde server now takes the url cleaner plugin into account.
    (Issue #54)

Thanks to @vincentbernat

*   Bug Fix: Ensure image sizer plugin handles external urls properly.
    (Issue #52)

Thanks to @rfk

*   Added PyPI publisher (Issue #49)
*   Bug Fix: Made `site.full_url` ignore fully qualified paths (Issue #49)

Thanks to @vincentbernat

*   Added JPEG Optim plugin (Issue #47)
*   Fixes to CLTransformer (Issue #47)

Version 0.8.2
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
*   Bug Fix: Made sorting tests more predictable (Issue #41)
*   Bug Fix: Added more standard paths for executables (Issue #41)
*   Added Combine files plugin (Issue #39)
*   Added ignore option in site configuration to igore based on wildcards
    (Issue #32)

Thanks to @pestaa

*   Added support `UTF8` keys in `metadata` and `config` (Issue #33)


Version 0.8.1
============================================================

Thanks to @rfk.

*   Updated to use nose 1.0 (Issue #28)
*   Bug fix: LessCSSPlugin: return original text if not a .less file
    (Issue #28)
*   PyFS publisher with mtime and etags support. (Issue #28)

Version 0.8
============================================================

*   Relative path bugs in windows generation have been fixed.

Version 0.8rc3
============================================================

*   Fixed a jinja2 loader path issue that prevented site generation in windows
*   Fixed tests for stylus plugin to account for more accurate color
    manipulation in the latest stylus
