# -*- coding: utf-8 -*-
"""
Contains classes and utilities for serving a site
generated from hyde.
"""
import threading
import urlparse
import urllib
import traceback
from datetime import datetime
from SimpleHTTPServer import SimpleHTTPRequestHandler
from BaseHTTPServer import HTTPServer

from hyde.generator import Generator

from fswrap import File, Folder

from commando.util import getLoggerWithNullHandler
logger = getLoggerWithNullHandler('hyde.server')

class HydeRequestHandler(SimpleHTTPRequestHandler):
    """
    Serves files by regenerating the resource (or)
    everything when a request is issued.
    """

    def do_GET(self):
        """
        Identify the requested path. If the query string
        contains `refresh`, regenerat the entire site.
        Otherwise, regenerate only the requested resource
        and serve.
        """
        self.server.request_time = datetime.now()
        logger.debug("Processing request: [%s]" % self.path)
        result = urlparse.urlparse(self.path)
        query = urlparse.parse_qs(result.query)
        if 'refresh' in query or result.query=='refresh':
            self.server.regenerate()
            if 'refresh' in query:
                del query['refresh']
            parts = list(tuple(result))
            parts[4] = urllib.urlencode(query)
            parts = tuple(parts)
            new_url = urlparse.urlunparse(parts)
            logger.info('Redirecting... [%s]' % new_url)
            self.redirect(new_url)
        else:
            SimpleHTTPRequestHandler.do_GET(self)


    def translate_path(self, path):
        """
        Finds the absolute path of the requested file by
        referring to the `site` variable in the server.
        """
        site = self.server.site
        result = urlparse.urlparse(urllib.unquote(self.path).decode('utf-8'))
        logger.debug("Trying to load file based on request: [%s]" % result.path)
        path = result.path.lstrip('/')
        res = None
        if path.strip() == "" or File(path).kind.strip() == "":
            deployed = site.config.deploy_root_path.child(path)
            deployed = Folder.file_or_folder(deployed)
            if isinstance(deployed, Folder):
                node = site.content.node_from_relative_path(path)
                res = node.get_resource('index.html')
            elif hasattr(site.config, 'urlcleaner') and hasattr(site.config.urlcleaner, 'strip_extensions'):
                for ext in site.config.urlcleaner.strip_extensions:
                    res = site.content.resource_from_relative_deploy_path(path + '.' + ext)
                    if res:
                        break
                for ext in site.config.urlcleaner.strip_extensions:
                    new_path = site.config.deploy_root_path.child(path + '.' + ext)
                    if File(new_path).exists:
                        return new_path
        else:
            res = site.content.resource_from_relative_deploy_path(path)

        if not res:
            logger.error("Cannot load file: [%s]" % path)
            return site.config.deploy_root_path.child(path)
        else:
            self.server.generate_resource(res)
        new_path = site.config.deploy_root_path.child(
                    res.relative_deploy_path)
        return new_path

    def do_404(self):
        """
        Sends a 'not found' response.
        """
        site = self.server.site
        if self.path != site.config.not_found:
            self.redirect(site.config.not_found)
        else:
            res = site.content.resource_from_relative_deploy_path(
                    site.config.not_found)

            message = "Requested resource not found"
            if not res:
                logger.error(
                    "Cannot find the 404 template [%s]."
                        % site.config.not_found)
            else:
                f404 = File(self.translate_path(site.config.not_found))
                if f404.exists:
                    message = f404.read_all()
            self.send_response(200, message)

    def redirect(self, path, temporary=True):
        """
        Sends a redirect header with the new location.
        """
        self.send_response(302 if temporary else 301)
        self.send_header('Location', path)
        self.end_headers()


class HydeWebServer(HTTPServer):
    """
    The hyde web server that regenerates the resource, node or site when
    a request is issued.
    """

    def __init__(self, site, address, port):
        self.site = site
        self.site.load()
        self.generator = Generator(self.site)
        self.request_time = datetime.strptime('1-1-1999', '%m-%d-%Y')
        self.regeneration_time = datetime.strptime('1-1-1998', '%m-%d-%Y')
        self.__is_shut_down = threading.Event()
        self.__shutdown_request = False
        self.map_extensions()
        HTTPServer.__init__(self, (address, port),
                                            HydeRequestHandler)

    def map_extensions(self):
        """
        Maps extensions specified in the configuration.
        """
        try:
            extensions = self.site.config.server.extensions.to_dict()
        except AttributeError:
            extensions = {}

        for extension, type in extensions.iteritems():
            ext = "." + extension if not extension == 'default' else ''
            HydeRequestHandler.extensions_map[ext] = type

    def regenerate(self):
        """
        Regenerates the entire site.
        """
        try:
            logger.info('Regenerating the entire site')
            self.regeneration_time = datetime.now()
            if self.site.config.needs_refresh():
                self.site.config.reload()
            self.site.load()
            self.generator.generate_all(incremental=False)
        except Exception, exception:
            logger.error('Error occured when regenerating the site [%s]'
                            % exception.message)
            logger.debug(traceback.format_exc())

    def generate_node(self, node):
        """
        Generates the given node.
        """

        deploy = self.site.config.deploy_root_path
        if not deploy.exists:
            return self.regenerate()

        try:
            logger.debug('Serving node [%s]' % node)
            self.generator.generate_node(node, incremental=True)
        except Exception, exception:
            logger.error(
                'Error [%s] occured when generating the node [%s]'
                        % (repr(exception), node))
            logger.debug(traceback.format_exc())

    def generate_resource(self, resource):
        """
        Regenerates the given resource.
        """
        deploy = self.site.config.deploy_root_path
        if not deploy.exists:
            return self.regenerate()
        dest = deploy.child_folder(resource.node.relative_path)
        if not dest.exists:
            return self.generate_node(resource.node)
        try:
            logger.debug('Serving resource [%s]' % resource)
            self.generator.generate_resource(resource, incremental=True)
        except Exception, exception:
            logger.error(
                'Error [%s] occured when serving the resource [%s]'
                        % (repr(exception), resource))
            logger.debug(traceback.format_exc())
