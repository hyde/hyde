Version 0.8.3
================

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
=============

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
=============

Thanks to @rfk.

*   Updated to use nose 1.0 (Issue #28)
*   Bug fix: LessCSSPlugin: return original text if not a .less file
    (Issue #28)
*   PyFS publisher with mtime and etags support. (Issue #28)

Version 0.8
==============

*   Relative path bugs in windows generation have been fixed.

Version 0.8rc3
==============

*   Fixed a jinja2 loader path issue that prevented site generation in windows
*   Fixed tests for stylus plugin to account for more accurate color
    manipulation in the latest stylus
