Requirements
============

All the python requirements are enumerated in dev-req.txt. You can install them
with:

::
    pip install -r dev-req.txt


Apart from these requirements the following are required by plugins if you
choose to run the corresponding tests. Some of the commands use the Mac OS X
package manager `homebrew` - please use the package manager corresponding to
your operating system.

Note: asciidoc is currently not tested, so the steps corresponding to that
format are unnecessary.

less and stylus also give test errors, so they are considered unsupported
until the corresponding issue (https://github.com/jgoldfar/hyde/issues/1) can
be addressed.

::
    npm install

    #asciidoc
    brew install asciidoc # or apt-get install asciidoc
    cd /usr/local/Cellar/asciidoc/8.6.8/bin
    curl -O https://asciidoc.googlecode.com/hg/asciidocapi.py

    #optipng
    brew install optipng # or apt-get install optipng


Ensure that `asciidoc`_ python api is available in the python path.

For example:

::
    export PYTHONPATH=/usr/local/Cellar/asciidoc/8.6.8/bin:$PYTHONPATH


Run the tests
=============

::
    nose2 tests
