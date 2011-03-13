Version 0.8b1

# A brand new **hyde**

This is the new version of hyde under active development. Hyde documentation
is a work in progress and can be found [here](http://hyde.github.com).

## Installation

To get the latest released version:

    pip install hyde

For the current trunk:

    pip install -e git://github.com/hyde/hyde.git#egg=hyde

## Creating a new hyde site

The following command:

        hyde -s ~/test_site create

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


## Examples

1. [Hyde Documentation](https://github.com/hyde/docs)
2. [Cloudpanic](https://github.com/tipiirai/cloudpanic)
3. [Ringce](https://github.com/lakshmivyas/ringce/tree/v3.0)

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
2. <del>Default Layouts</del>
3. Django Support
4. Plugins:
    * <del>Tags</del>
    * Atom / RSS
    * <del>Text Compressor (CSS, JS, HTML)</del>
    * <del>Image optimizer</del>