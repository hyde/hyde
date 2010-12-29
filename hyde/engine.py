# -*- coding: utf-8 -*-
"""
Implements the hyde entry point commands
"""
from commando import *
from hyde.exceptions import HydeException
from hyde.fs import File, Folder
from hyde.layout import Layout, HYDE_DATA
from hyde.model import Config
from hyde.site import Site
from hyde.version import __version__

import logging
import os
import yaml

HYDE_LAYOUTS = "HYDE_LAYOUTS"

logger = logging.getLogger('hyde.engine')
logger.setLevel(logging.DEBUG)

import sys
logger.addHandler(logging.StreamHandler(sys.stdout))

class Engine(Application):
    """
    The Hyde Application
    """

    @command(description='hyde - a python static website generator',
            epilog='Use %(prog)s {command} -h to get help on individual commands')
    @version('-v', '--version', version='%(prog)s ' + __version__)
    @store('-s', '--sitepath', default='.', help="Location of the hyde site")
    def main(self, args):
        """
        Will not be executed. A sub command is required. This function exists to provide
        common parameters for the subcommands and some generic stuff like version and
        metadata
        """
        pass

    @subcommand('create', help='Create a new hyde site')
    @store('-l', '--layout', default='basic', help='Layout for the new site')
    @true('-f', '--force', default=False, dest='overwrite',
                                          help='Overwrite the current site if it exists')
    def create(self, args):
        """
        The create command. Creates a new site from the template at the given
        sitepath.
        """
        sitepath = Folder(args.sitepath)
        if sitepath.exists and not args.overwrite:
            raise HydeException("The given site path[%s] is not empty" % sitepath)
        layout = Layout.find_layout(args.layout)
        logger.info("Creating site at [%s] with layout [%s]" % (sitepath, layout))
        if not layout or not layout.exists:
            raise HydeException(
            "The given layout is invalid. Please check if you have the `layout` "
            "in the right place and the environment variable(%s) has been setup "
            "properly if you are using custom path for layouts" % HYDE_DATA)
        layout.copy_contents_to(args.sitepath)
        logger.info("Site creation complete")

    @subcommand('gen', help='Generate the site')
    @store('-c', '--config-path', default='site.yaml', dest='config',
            help='The configuration used to generate the site')
    @store('-d', '--deploy-path', default='deploy', help='Where should the site be generated?')
    def gen(self, args):
        """
        The generate command. Generates the site at the given deployment directory.
        """
        sitepath = Folder(args.sitepath)
        logger.info("Generating site at [%s]" % sitepath)
        # Read the configuration
        config_file = sitepath.child(args.config)
        logger.info("Reading site configuration from [%s]", config_file)
        conf = {}
        with open(config_file) as stream:
            conf = yaml.load(stream)
        site = Site(sitepath, Config(sitepath, conf))
        # TODO: Find the appropriate template environment
        from hyde.ext.templates.jinja import Jinja2Template
        template = Jinja2Template(sitepath)
        logger.info("Using [%s] as the template", template)
        # Configure the environment
        logger.info("Configuring Template environment")
        template.configure(site.config)
        # Prepare site info
        logger.info("Analyzing site contents")
        site.build()
        context = dict(site=site)
        # Generate site one file at a time
        logger.info("Generating site to [%s]" % site.config.deploy_root_path)
        for page in site.content.walk_resources():
            logger.info("Processing [%s]", page)
            target = File(page.source_file.get_mirror(site.config.deploy_root_path, site.content.source_folder))
            target.parent.make()
            if page.source_file.is_text:
                logger.info("Rendering [%s]", page)
                context.update(page=page)
                text = template.render(page.source_file.read_all(), context)
                target.write(text)
            else:
                logger.info("Copying binary file [%s]", page)
                page.source_file.copy_to(target)