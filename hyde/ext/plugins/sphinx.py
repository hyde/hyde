# -*- coding: utf-8 -*-
"""
Sphinx plugin.

This plugin lets you easily include sphinx-generated documentation as part
of your Hyde site.
"""

from __future__ import absolute_import

import json
import tempfile 

from hyde.plugin import Plugin
from hyde.fs import File, Folder
from hyde.model import Expando

import sphinx


class SphinxPlugin(Plugin):
    """The plugin class for rendering sphinx-generated documentation."""

    def __init__(self, site):
        self.sphinx_build_dir = None
        super(SphinxPlugin, self).__init__(site)

    @property
    def plugin_name(self):
        return "sphinx"

    @property
    def settings(self):
        settings = Expando({})
        settings.conf_path = "."
        settings.block_map = Expando({})
        settings.block_map.body = "body"
        try:
            user_settings = getattr(self.site.config, self.plugin_name)
        except AttributeError:
            pass
        else:
            for name in dir(user_settings):
                if not name.startswith("_"):
                    setattr(settings,name,getattr(user_settings,name))
        return settings

    def begin_site(self):
        #  Find and adjust all the resource that will be handled by sphinx.
        #  We need to:
        #    * change the deploy name from .rst to .html
        #    * make sure they don't get rendered inside a default block
        for resource in self.site.content.walk_resources():
            if resource.source_file.kind == "rst":
                new_name = resource.source_file.name_without_extension + ".html"
                target_folder = File(resource.relative_deploy_path).parent
                resource.relative_deploy_path = target_folder.child(new_name)
                resource.meta.default_block = None

    def begin_text_resource(self,resource,text):
        """If this is a sphinx input file, replace it with the generated docs.

        This method will replace the text of the file with the sphinx-generated
        documentation, lazily running sphinx if it has not yet been called.
        """
        if resource.source_file.kind != "rst":
            return text
        if self.sphinx_build_dir is None:
            self._run_sphinx()
        output = []
        settings = self.settings
        for (nm,content) in self._get_sphinx_output(resource).iteritems():
            try:
                block = getattr(settings.block_map,nm)
            except AttributeError:
                pass
            else:
                output.append("{%% block %s %%}" % (block,))
                output.append(content)
                output.append("{% endblock %}")
        return "\n".join(output)

    def site_complete(self):
        if self.sphinx_build_dir is not None:
            self.sphinx_build_dir.delete()

    def _run_sphinx(self):
        """Run sphinx to generate the necessary output files.

        This method creates a temporary directory, copies all sphinx-related
        files into it, and then runs the sphinx build process to produce
        the documentation fragments.
        """
        self.sphinx_build_dir = Folder(tempfile.mkdtemp())
        #  Copy all sphinx files into a temporary build directory.
        self.sphinx_input_dir = self.sphinx_build_dir.child_folder("input")
        self.sphinx_input_dir.make()
        for resource in self.site.content.walk_resources():
            if resource.source_file.kind == "rst":
                relpath = resource.relative_path
                build_file = File(self.sphinx_input_dir.child(relpath))
                build_file.parent.make()
                resource.source_file.copy_to(build_file)
        #  Run sphinx to generate output in the output directory.
        self.sphinx_output_dir = self.sphinx_build_dir.child_folder("output")
        self.sphinx_output_dir.make()
        conf_path = self.site.sitepath.child_folder(self.settings.conf_path)
        sphinx_args = ["sphinx-build"]
        sphinx_args.extend([
            "-b", "json",
            "-c", conf_path.path,
            self.sphinx_input_dir.path,
            self.sphinx_output_dir.path
        ])
        if sphinx.main(sphinx_args) != 0:
            raise RuntimeError("sphinx build failed")

    def _get_sphinx_output(self,resource):
        relpath = File(resource.relative_path)
        relpath = relpath.parent.child(relpath.name_without_extension+".fjson")
        with open(self.sphinx_output_dir.child(relpath),"rb") as f:
            return json.load(f)

