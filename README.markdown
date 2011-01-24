# A brand new **hyde**

This is the new version of hyde under active development.
I haven't managed to document the features yet. [This][hyde1-0] should
give a good understanding of the motivation behind this version. You can
also take a look at the [cloudpanic source][cp] for a reference implementation.

[hyde1-0]: http://groups.google.com/group/hyde-dev/web/hyde-1-0
[cp]: http://github.com/tipiirai/cloudpanic/tree/refactor

[Here](http://groups.google.com/group/hyde-dev/browse_thread/thread/2a143bd2081b3322) is
the initial announcement of the project.

## Installation

Hyde supports both python 2.7 and 2.6.

        pip install -r req-2.6.txt

or

        pip install -r req-2.7.txt


will install all the dependencies of hyde.

You can choose to install hyde by running

        python setup.py install

## Creating a new hyde site

The new version of Hyde uses the `argparse` module and hence support subcommands.


        hyde -s ~/test_site create -l test

will create a new hyde site using the test layout.


## Generating the hyde site

        cd ~/test_site
        hyde gen

## Serving the website

        cd ~/test_site
        hyde serve
        open http://localhost:8080


The server also regenerates on demand. As long as the server is running,
you can make changes to your source and refresh the browser to view the changes.


## A brief list of features


1. Support for multiple templates (although only `Jinja2` is currently implemented)
2. The different processor modules in the previous version are now
   replaced by a plugin object. This allows plugins to listen to events that
   occur during different times in the lifecycle and respond accordingly.
3. Metadata: Hyde now supports hierarchical metadata. You can specify and override
   variables at the site, node or the page level and access them in the templates.
4. Sorting: The sorter plugin provides rich sorting options that extend the
   object model.
5. Syntactic Sugar: Because of the richness of the plugin infrastructure, hyde can
   now provide additional syntactic sugar to make the content more readable. See
   `blockdown` and `autoextend` plugin for examples.

## Next Steps

1. Documentation
2. Default Layouts
3. Django Support
4. Plugins:
    * Tags
    * Atom / RSS
    * Text Compressor (CSS, JS, HTML)
    * Image optimizer