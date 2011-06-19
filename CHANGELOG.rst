Version 0.8.3c4
===============

Thanks to @gfuchedzhy

*   Bug Fix: Hyde server now takes the url cleaner plugin into account.

Version 0.8.3c3
===============

Thanks to @vincentbernat

*   Bug Fix: Ensure image sizer plugin handles external urls properly.

Version 0.8.3c2
================

Thanks to @rfk

*   Added PyPI publisher
*   Bug Fix: Made `site.full_url` ignore fully qualified paths

Version 0.8.3c1
================

Thanks to @vincentbernat

*   Added JPEG Optim plugin
*   Fixes to CLTransformer

Version 0.8.2
=============

Thanks to @merlinrebrovic

*   Added hyde starter kit

Thanks to @vincentbernat

*   Added git dates plugin
*   Added Image size plugin
*   Added silent, compress and optimization parameter support for less css plugin
*   Fixed plugin chaining issues
*   Added Language(translation) plugin
*   Bug Fix: Made sorting tests more predictable
*   Bug Fix: Added more standard paths for executables
*   Added Combine files plugin
*   Added ignore option in site configuration to igore based on wildcards

Thanks to @pestaa

*   Added support `UTF8` keys in `metadata` and `config`


Version 0.8.1
=============

Thanks to @rfk.

*   Updated to use nose 1.0
*   Bug fix: LessCSSPlugin: return original text if not a .less file
*   PyFS publisher with mtime and etags support.

Version 0.8
==============

*   Relative path bugs in windows generation have been fixed.

Version 0.8rc3
==============

*   Fixed a jinja2 loader path issue that prevented site generation in windows
*   Fixed tests for stylus plugin to account for more accurate color
    manipulation in the latest stylus
