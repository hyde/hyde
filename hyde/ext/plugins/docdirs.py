# -*- coding: utf-8 -*-
"""
Interpret all subdirectories in particular directory as Sphinx sources.

This plugin lets you easily include sphinx-generated documentation as part
of your Hyde site.  It is simultaneously a Hyde plugin and a Sphinx plugin.

To make this work, you need to:

    * install sphinx, obviously
    * create `docs` subdirectory
    * put sphinx sources in subdirectory of `docs` directory

For example you might have your site set up like this::

    site.yaml    <--  hyde config file
    conf.py      <--  sphinx config file
    contents/
        index.html     <-- non-sphinx files, handled by hyde
        other.html
        docs/
            project1/
                index.rst      <-- files to processed by sphinx
                mymodule.rst
            project2/
                index.rst      <-- files to processed by sphinx
                mymodule.rst
"""

#  We need absolute import so that we can import the main "sphinx"
#  module even though this module is also called "sphinx". Ugh.
from __future__ import absolute_import

import os
import json
import tempfile

from hyde.plugin import Plugin
from hyde.fs import File, Folder
from hyde.ext.plugins.meta import  Metadata

from hyde.util import getLoggerWithNullHandler

logger = getLoggerWithNullHandler('hyde.ext.plugins.sphinx')

try:
    from sphinx.application import Sphinx
    from sphinx.builders.html import JSONHTMLBuilder
    from sphinx.util.osutil import SEP
except ImportError:
    logger.error("The sphinx plugin requires sphinx.")
    logger.error("`pip install -U sphinx` to get it.")
    raise


class SphinxGenerator(object):
    def __init__(self, node, settings):
        self.__node = node
        self.__config = None
        self.__build_dir = None
        self.__settings = settings
        self.__layout = self.__settings.get("layout", "sphinx.j2")

    def node(self):
        return self.__node

    def config(self):
        if self.__config is None:
            #  Sphinx always execs the config file in its parent dir.
            conf_file = os.path.join(self.__node.path, "conf.py")
            self.__config = {"__file__": conf_file}
            curdir = os.getcwd()
            os.chdir(self.__node.path)
            try:
                execfile(conf_file, self.__config)
            finally:
                os.chdir(curdir)
        return self.__config

    def fix_generated_filenames(self):
        suffix = self.config().get("source_suffix", ".rst")
        for resource in self.__node.walk_resources():
            if resource.source_file.path.endswith(suffix):
                new_name = resource.source_file.name_without_extension + ".html"
                target_folder = File(resource.relative_deploy_path).parent
                resource.relative_deploy_path = target_folder.child(new_name)
                if self.__settings.get("block_map", None):
                    resource.meta.default_block = None

    def generate_resource(self, resource, text):
        suffix = self.config().get("source_suffix", ".rst")
        if not resource.source_file.path.endswith(suffix):
            return "".join(("{% raw %}", text, "{% endraw %}"))
        if self.__build_dir is None:
            self.__run_sphinx()

        output = [
            "---\n",
            "extends: {0}\n".format(self.__layout),
            "doc_root_url: {0}\n".format(self.node().get_relative_deploy_path()),
            "---\n\n"
        ]
        sphinx_output = self.__get_sphinx_output(resource)
        for name, content in sphinx_output.iteritems():
            if name in ("body", "toc"):
                output.append("{{% block {0} %}}{{% raw %}}".format(name))
                output.append(content)
                output.append("{% endraw %}{% endblock %}")
        self.__update_metadata(resource, {"sphinx": sphinx_output})
        return "".join(output)

    def clean(self):
        if self.__build_dir is not None:
            self.__build_dir.delete()

    def __run_sphinx(self):
        """Run sphinx to generate the necessary output files.

        This method creates a temporary directory for sphinx's output, then
        run sphinx against the Hyde input directory.
        """
        logger.info("running sphinx")
        self.__build_dir = Folder(tempfile.mkdtemp())
        sphinx_app = Sphinx(
            self.node().path,
            self.node().path,
            self.__build_dir.path,
            self.node().path,
            "json"
        )
        sphinx_app.add_builder(HydeJSONHTMLBuilder)
        sphinx_app._init_builder("hyde_json")
        sphinx_app.build()

    def __get_sphinx_output(self, resource):
        """Get the sphinx output for a given resource.

        This returns a dict mapping block names to HTML text fragments.
        The most important fragment is "body" which contains the main text
        of the document.  The other fragments are for things like navigation,
        related pages and so-on.
        """
        relpath = File(resource.relative_path)
        relpath = relpath.parent.child(relpath.name_without_extension + ".fjson")[len(self.node().relative_path) + 1:]
        with open(self.__build_dir.child(relpath), "rb") as f:
            return json.load(f)

    def __update_metadata(self, resource, metadata):
        if not hasattr(resource, 'meta') or not resource.meta:
            if not hasattr(resource.node, 'meta'):
                resource.node.meta = Metadata({})
            resource.meta = Metadata(metadata, resource.node.meta)
        else:
            resource.meta.update(metadata)


class DocdirsPlugin(Plugin):
    """The plugin class for rendering sphinx-generated documentation."""

    def __init__(self, site):
        self.generators = {}
        super(DocdirsPlugin, self).__init__(site)
        self.docsroot = self.settings.get("docsroot", "docs")

    def begin_node(self, node):
        settings = self.settings
        if File(node.relative_path).parent.path == self.docsroot:
            generator = SphinxGenerator(node, settings)
            generator.fix_generated_filenames()
            self.generators[node.name] = generator

    def begin_text_resource(self, resource, text):
        """Event hook for processing an individual resource.

        If the input resource is a sphinx input file, this method will replace
        replace the text of the file with the sphinx-generated documentation.

        Sphinx itself is run lazily the first time this method is called.
        This means that if no sphinx-related resources need updating, then
        we entirely avoid running sphinx.
        """
        generator = None
        for i, gen in self.generators.items():
            if resource.relative_path.startswith(os.path.join(self.docsroot, i) + "/"):
                generator = gen
                break

        if generator is None:
            return text

        return generator.generate_resource(resource, text)

    def site_complete(self):
        """Event hook for when site processing ends.

        This simply cleans up any temorary build file.
        """
        for generator in self.generators.values():
            generator.clean()


class HydeJSONHTMLBuilder(JSONHTMLBuilder):
    """A slightly-customised JSONHTMLBuilder, for use by Hyde.

    This is a Sphinx builder that serilises the generated HTML fragments into
    a JSON docuent, so they can be later retrieved and dealt with at will.

    The only customistion we do over the standard JSONHTMLBuilder is to 
    reference documents with a .html suffix, so that internal link will
    work correctly once things have been processed by Hyde.
    """
    name = "hyde_json"

    def get_target_uri(self, docname, typ=None):
        return docname + ".html"
