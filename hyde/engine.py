# -*- coding: utf-8 -*-
"""
Implements the hyde entry point commands
"""
from hyde.exceptions import HydeException
from hyde.layout import Layout, HYDE_DATA
from hyde.model import Config
from hyde.site import Site
from hyde.version import __version__

from commando import (
    Application,
    command,
    store,
    subcommand,
    true,
    version
)
from commando.util import getLoggerWithConsoleHandler
from fswrap import FS, Folder

HYDE_LAYOUTS = "HYDE_LAYOUTS"


class Engine(Application):

    def __init__(self, raise_exceptions=False):
        logger = getLoggerWithConsoleHandler('hyde')
        super(Engine, self).__init__(
            raise_exceptions=raise_exceptions,
            logger=logger
        )

    @command(description='hyde - a python static website generator',
        epilog='Use %(prog)s {command} -h to get help on individual commands')
    @true('-v', '--verbose', help="Show detailed information in console")
    @true('-x', '--raise-exceptions', default=None,
        help="Don't handle exceptions.")
    @version('--version', version='%(prog)s ' + __version__)
    @store('-s', '--sitepath', default='.', help="Location of the hyde site")
    def main(self, args):
        """
        Will not be executed. A sub command is required. This function exists
        to provide common parameters for the subcommands and some generic stuff
        like version and metadata
        """
        sitepath = Folder(args.sitepath).fully_expanded_path
        if args.raise_exceptions in (True, False):
            self.raise_exceptions = args.raise_exceptions
        return Folder(sitepath)

    @subcommand('create', help='Create a new hyde site.')
    @store('-l', '--layout', default='basic', help='Layout for the new site')
    @true('-f', '--force', default=False, dest='overwrite',
                            help='Overwrite the current site if it exists')
    def create(self, args):
        """
        The create command. Creates a new site from the template at the given
        sitepath.
        """
        sitepath = self.main(args)
        markers = ['content', 'layout', 'site.yaml']
        exists = any((FS(sitepath.child(item)).exists for item in markers))

        if exists and not args.overwrite:
            raise HydeException(
                    "The given site path [%s] already contains a hyde site."
                    " Use -f to overwrite." % sitepath)
        layout = Layout.find_layout(args.layout)
        self.logger.info(
            "Creating site at [%s] with layout [%s]" % (sitepath, layout))
        if not layout or not layout.exists:
            raise HydeException(
            "The given layout is invalid. Please check if you have the"
            " `layout` in the right place and the environment variable(%s)"
            " has been setup properly if you are using custom path for"
            " layouts" % HYDE_DATA)
        layout.copy_contents_to(args.sitepath)
        self.logger.info("Site creation complete")

    @subcommand('gen', help='Generate the site')
    @store('-c', '--config-path', default='site.yaml', dest='config',
            help='The configuration used to generate the site')
    @store('-d', '--deploy-path', dest='deploy', default=None,
                        help='Where should the site be generated?')
    @true('-r', '--regen', dest='regen', default=False,
                        help='Regenerate the whole site, including unchanged files')
    def gen(self, args):
        """
        The generate command. Generates the site at the given
        deployment directory.
        """
        sitepath = self.main(args)
        site = self.make_site(sitepath, args.config, args.deploy)
        from hyde.generator import Generator
        gen = Generator(site)
        incremental = True
        if args.regen:
            self.logger.info("Regenerating the site...")
            incremental = False
        gen.generate_all(incremental=incremental)
        self.logger.info("Generation complete.")

    @subcommand('serve', help='Serve the website')
    @store('-a', '--address', default='localhost', dest='address',
            help='The address where the website must be served from.')
    @store('-p', '--port', type=int, default=8080, dest='port',
            help='The port where the website must be served from.')
    @store('-c', '--config-path', default='site.yaml', dest='config',
            help='The configuration used to generate the site')
    @store('-d', '--deploy-path', dest='deploy', default=None,
                    help='Where should the site be generated?')
    def serve(self, args):
        """
        The serve command. Serves the site at the given
        deployment directory, address and port. Regenerates
        the entire site or specific files based on the request.
        """
        sitepath = self.main(args)
        site = self.make_site(sitepath, args.config, args.deploy)
        from hyde.server import HydeWebServer
        server = HydeWebServer(site, args.address, args.port)
        self.logger.info("Starting webserver at [%s]:[%d]", args.address, args.port)
        try:
            server.serve_forever()
        except (KeyboardInterrupt, SystemExit):
            self.logger.info("Received shutdown request. Shutting down...")
            server.shutdown()
            self.logger.info("Server successfully stopped")
            exit()

    @subcommand('publish', help='Publish the website')
    @store('-c', '--config-path', default='site.yaml', dest='config',
            help='The configuration used to generate the site')
    @store('-p', '--publisher', dest='publisher', default='default',
            help='Points to the publisher configuration.')
    @store('-m', '--message', dest='message',
            help='Optional message.')
    def publish(self, args):
        """
        Publishes the site based on the configuration from the `target`
        parameter.
        """
        sitepath = self.main(args)
        site = self.make_site(sitepath, args.config)
        from hyde.publisher import Publisher
        publisher = Publisher.load_publisher(site,
                        args.publisher,
                        args.message)
        publisher.publish()


    def make_site(self, sitepath, config, deploy=None):
        """
        Creates a site object from the given sitepath and the config file.
        """
        config = Config(sitepath, config_file=config)
        if deploy:
            config.deploy_root = deploy
        return Site(sitepath, config)