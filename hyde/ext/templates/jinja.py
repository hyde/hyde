# -*- coding: utf-8 -*-
"""
Jinja template utilties
"""

from datetime import datetime, date
import os
import re
import itertools
from urllib import quote, unquote

from hyde.fs import File, Folder
from hyde.model import Expando
from hyde.template import HtmlWrap, Template
from hyde.util import getLoggerWithNullHandler
from operator import attrgetter

from jinja2 import contextfunction, Environment
from jinja2 import FileSystemLoader, FileSystemBytecodeCache
from jinja2 import contextfilter, environmentfilter, Markup, Undefined, nodes
from jinja2.ext import Extension
from jinja2.exceptions import TemplateError

logger = getLoggerWithNullHandler('hyde.engine.Jinja2')

class SilentUndefined(Undefined):
    """
    A redefinition of undefined that eats errors.
    """
    def __getattr__(self, name):
        return self

    __getitem__ = __getattr__

    def __call__(self, *args, **kwargs):
        return self

@contextfunction
def media_url(context, path):
    """
    Returns the media url given a partial path.
    """
    return context['site'].media_url(path)

@contextfunction
def content_url(context, path):
    """
    Returns the content url given a partial path.
    """
    return context['site'].content_url(path)

@contextfunction
def full_url(context, path):
    """
    Returns the full url given a partial path.
    """
    return context['site'].full_url(path)

@contextfilter
def urlencode(ctx, url):
    return quote(url.encode('utf8'))

@contextfilter
def urldecode(ctx, url):
    return unquote(url).decode('utf8')

@contextfilter
def date_format(ctx, dt, fmt=None):
    if not dt:
        dt = datetime.now()
    if not isinstance(dt, datetime) or \
        not isinstance(dt, date):
        logger.error("Date format called on a non date object")
        return dt

    format = fmt or "%a, %d %b %Y"
    if not fmt:
        global_format = ctx.resolve('dateformat')
        if not isinstance(global_format, Undefined):
            format = global_format
    return dt.strftime(format)


def islice(iterable, start=0, stop=3, step=1):
    return itertools.islice(iterable, start, stop, step)

def top(iterable, count=3):
    return islice(iterable, stop=count)

def xmldatetime(dt):
    if not dt:
        dt = datetime.now()
    zprefix = "Z"
    tz = dt.strftime("%z")
    if tz:
        zprefix = tz[:3] + ":" + tz[3:]
    return dt.strftime("%Y-%m-%dT%H:%M:%S") + zprefix

@environmentfilter
def asciidoc(env, value):
    """
    (simple) Asciidoc filter
    """
    try:
        from asciidocapi import AsciiDocAPI
    except ImportError:
        print u"Requires AsciiDoc library to use AsciiDoc tag."
        raise

    import StringIO
    output = value

    asciidoc = AsciiDocAPI()
    asciidoc.options('--no-header-footer')
    result = StringIO.StringIO()
    asciidoc.execute(StringIO.StringIO(output.encode('utf-8')), result, backend='html4')
    return unicode(result.getvalue(), "utf-8")

@environmentfilter
def markdown(env, value):
    """
    Markdown filter with support for extensions.
    """
    try:
        import markdown as md
    except ImportError:
        logger.error(u"Cannot load the markdown library.")
        raise TemplateError(u"Cannot load the markdown library")
    output = value
    d = {}
    if hasattr(env.config, 'markdown'):
        d['extensions'] = getattr(env.config.markdown, 'extensions', [])
        d['extension_configs'] = getattr(env.config.markdown,
                                        'extension_configs',
                                        Expando({})).to_dict()
        if hasattr(env.config.markdown, 'output_format'):
            d['output_format'] = env.config.markdown.output_format
    marked = md.Markdown(**d)

    return marked.convert(output)

@environmentfilter
def restructuredtext(env, value):
    """
    RestructuredText filter
    """
    try:
        from docutils.core import publish_parts
    except ImportError:
        logger.error(u"Cannot load the docutils library.")
        raise TemplateError(u"Cannot load the docutils library.")

    highlight_source = False
    if hasattr(env.config, 'restructuredtext'):
        highlight_source = getattr(env.config.restructuredtext, 'highlight_source', False)

    if highlight_source:
        import hyde.lib.pygments.rst_directive

    parts = publish_parts(source=value, writer_name="html")
    return parts['html_body']

@environmentfilter
def syntax(env, value, lexer=None, filename=None):
    """
    Processes the contained block using `pygments`
    """
    try:
        import pygments
        from pygments import lexers
        from pygments import formatters
    except ImportError:
        logger.error(u"pygments library is required to"
                        " use syntax highlighting tags.")
        raise TemplateError("Cannot load pygments")

    pyg = (lexers.get_lexer_by_name(lexer)
                if lexer else
                    lexers.guess_lexer(value))
    settings = {}
    if hasattr(env.config, 'syntax'):
        settings = getattr(env.config.syntax,
                            'options',
                            Expando({})).to_dict()

    formatter = formatters.HtmlFormatter(**settings)
    code = pygments.highlight(value, pyg, formatter)
    code = code.replace('\n\n', '\n&nbsp;\n').replace('\n', '<br />')
    caption = filename if filename else pyg.name
    if hasattr(env.config, 'syntax'):
        if not getattr(env.config.syntax, 'use_figure', True):
            return Markup(code)
    return Markup(
            '<div class="codebox"><figure class="code">%s<figcaption>%s</figcaption></figure></div>\n\n'
                        % (code, caption))

class Spaceless(Extension):
    """
    Emulates the django spaceless template tag.
    """

    tags = set(['spaceless'])

    def parse(self, parser):
        """
        Parses the statements and calls back to strip spaces.
        """
        lineno = parser.stream.next().lineno
        body = parser.parse_statements(['name:endspaceless'],
                drop_needle=True)
        return nodes.CallBlock(
                    self.call_method('_render_spaceless'),
                    [], [], body).set_lineno(lineno)

    def _render_spaceless(self, caller=None):
        """
        Strip the spaces between tags using the regular expression
        from django. Stolen from `django.util.html` Returns the given HTML
        with spaces between tags removed.
        """
        if not caller:
            return ''
        return re.sub(r'>\s+<', '><', unicode(caller().strip()))

class Asciidoc(Extension):
    """
    A wrapper around the asciidoc filter for syntactic sugar.
    """
    tags = set(['asciidoc'])

    def parse(self, parser):
        """
        Parses the statements and defers to the callback for asciidoc processing.
        """
        lineno = parser.stream.next().lineno
        body = parser.parse_statements(['name:endasciidoc'], drop_needle=True)

        return nodes.CallBlock(
                    self.call_method('_render_asciidoc'),
                        [], [], body).set_lineno(lineno)

    def _render_asciidoc(self, caller=None):
        """
        Calls the asciidoc filter to transform the output.
        """
        if not caller:
            return ''
        output = caller().strip()
        return asciidoc(self.environment, output)

class Markdown(Extension):
    """
    A wrapper around the markdown filter for syntactic sugar.
    """
    tags = set(['markdown'])

    def parse(self, parser):
        """
        Parses the statements and defers to the callback for markdown processing.
        """
        lineno = parser.stream.next().lineno
        body = parser.parse_statements(['name:endmarkdown'], drop_needle=True)

        return nodes.CallBlock(
                    self.call_method('_render_markdown'),
                        [], [], body).set_lineno(lineno)

    def _render_markdown(self, caller=None):
        """
        Calls the markdown filter to transform the output.
        """
        if not caller:
            return ''
        output = caller().strip()
        return markdown(self.environment, output)

class restructuredText(Extension):
    """
    A wrapper around the restructuredtext filter for syntactic sugar
    """
    tags = set(['restructuredtext'])

    def parse(self, parser):
        """
        Simply extract our content
        """
        lineno = parser.stream.next().lineno
        body = parser.parse_statements(['name:endrestructuredtext'], drop_needle=True)

        return nodes.CallBlock(self.call_method('_render_rst'), [],  [], body
                              ).set_lineno(lineno)

    def _render_rst(self, caller=None):
        """
        call our restructuredtext filter
        """
        if not caller:
            return ''
        output = caller().strip()
        return restructuredtext(self.environment, output)

class YamlVar(Extension):
    """
    An extension that converts the content between the tags
    into an yaml object and sets the value in the given
    variable.
    """

    tags = set(['yaml'])

    def parse(self, parser):
        """
        Parses the contained data and defers to the callback to load it as
        yaml.
        """
        lineno = parser.stream.next().lineno
        var = parser.stream.expect('name').value
        body = parser.parse_statements(['name:endyaml'], drop_needle=True)
        return [
                nodes.Assign(
                    nodes.Name(var, 'store'),
                    nodes.Const({})
                    ).set_lineno(lineno),
                nodes.CallBlock(
                    self.call_method('_set_yaml',
                            args=[nodes.Name(var, 'load')]),
                            [], [], body).set_lineno(lineno)
                ]


    def _set_yaml(self, var, caller=None):
        """
        Loads the yaml data into the specified variable.
        """
        if not caller:
            return ''
        try:
            import yaml
        except ImportError:
            return ''

        out = caller().strip()
        var.update(yaml.load(out))
        return ''

def parse_kwargs(parser):
    """
    Parses keyword arguments in tags.
    """
    name = parser.stream.expect('name').value
    parser.stream.expect('assign')
    if parser.stream.current.test('string'):
        value = parser.parse_expression()
    else:
        value = nodes.Const(parser.stream.next().value)
    return (name, value)

class Syntax(Extension):
    """
    A wrapper around the syntax filter for syntactic sugar.
    """

    tags = set(['syntax'])


    def parse(self, parser):
        """
        Parses the statements and defers to the callback for pygments processing.
        """
        lineno = parser.stream.next().lineno
        lex = nodes.Const(None)
        filename = nodes.Const(None)

        if not parser.stream.current.test('block_end'):
            if parser.stream.look().test('assign'):
                name = value = value1 = None
                (name, value) = parse_kwargs(parser)
                if parser.stream.skip_if('comma'):
                    (_, value1) = parse_kwargs(parser)

                (lex, filename) = (value, value1) \
                                        if name == 'lex' \
                                            else (value1, value)
            else:
                lex = nodes.Const(parser.stream.next().value)
                if parser.stream.skip_if('comma'):
                    filename = parser.parse_expression()

        body = parser.parse_statements(['name:endsyntax'], drop_needle=True)
        return nodes.CallBlock(
                    self.call_method('_render_syntax',
                        args=[lex, filename]),
                        [], [], body).set_lineno(lineno)


    def _render_syntax(self, lex, filename, caller=None):
        """
        Calls the syntax filter to transform the output.
        """
        if not caller:
            return ''
        output = caller().strip()
        return syntax(self.environment, output, lex, filename)

class IncludeText(Extension):
    """
    Automatically runs `markdown` and `typogrify` on included
    files.
    """

    tags = set(['includetext'])

    def parse(self, parser):
        """
        Delegates all the parsing to the native include node.
        """
        node = parser.parse_include()
        return nodes.CallBlock(
                    self.call_method('_render_include_text'),
                        [], [], [node]).set_lineno(node.lineno)

    def _render_include_text(self, caller=None):
        """
        Runs markdown and if available, typogrigy on the
        content returned by the include node.
        """
        if not caller:
            return ''
        output = caller().strip()
        output = markdown(self.environment, output)
        if 'typogrify' in self.environment.filters:
            typo = self.environment.filters['typogrify']
            output = typo(output)
        return output

MARKINGS = '_markings_'

class Reference(Extension):
    """
    Marks a block in a template such that its available for use
    when referenced using a `refer` tag.
    """

    tags = set(['mark', 'reference'])

    def parse(self, parser):
        """
        Parse the variable name that the content must be assigned to.
        """
        token = parser.stream.next()
        lineno = token.lineno
        tag = token.value
        name = parser.stream.next().value
        body = parser.parse_statements(['name:end%s' % tag], drop_needle=True)
        return nodes.CallBlock(
                    self.call_method('_render_output',
                        args=[nodes.Name(MARKINGS, 'load'), nodes.Const(name)]),
                        [], [], body).set_lineno(lineno)


    def _render_output(self, markings, name, caller=None):
        """
        Assigns the result of the contents to the markings variable.
        """
        if not caller:
            return ''
        out = caller()
        if isinstance(markings, dict):
            markings[name] = out
        return out

class Refer(Extension):
    """
    Imports content blocks specified in the referred template as
    variables in a given namespace.
    """
    tags = set(['refer'])

    def parse(self, parser):
        """
        Parse the referred template and the namespace.
        """
        token = parser.stream.next()
        lineno = token.lineno
        parser.stream.expect('name:to')
        template = parser.parse_expression()
        parser.stream.expect('name:as')
        namespace = parser.stream.next().value
        includeNode = nodes.Include(lineno=lineno)
        includeNode.with_context = True
        includeNode.ignore_missing = False
        includeNode.template = template

        temp = parser.free_identifier(lineno)

        return [
                nodes.Assign(
                    nodes.Name(temp.name, 'store'),
                    nodes.Name(MARKINGS, 'load')
                ).set_lineno(lineno),
                nodes.Assign(
                    nodes.Name(MARKINGS, 'store'),
                    nodes.Const({})).set_lineno(lineno),
                nodes.Assign(
                    nodes.Name(namespace, 'store'),
                    nodes.Const({})).set_lineno(lineno),
                nodes.CallBlock(
                    self.call_method('_push_resource',
                            args=[
                                nodes.Name(namespace, 'load'),
                                nodes.Name('site', 'load'),
                                nodes.Name('resource', 'load'),
                                template]),
                            [], [], []).set_lineno(lineno),
                nodes.Assign(
                    nodes.Name('resource', 'store'),
                    nodes.Getitem(nodes.Name(namespace, 'load'),
                        nodes.Const('resource'), 'load')
                    ).set_lineno(lineno),
                nodes.CallBlock(
                    self.call_method('_assign_reference',
                            args=[
                                nodes.Name(MARKINGS, 'load'),
                                nodes.Name(namespace, 'load')]),
                            [], [], [includeNode]).set_lineno(lineno),
                nodes.Assign(nodes.Name('resource', 'store'),
                            nodes.Getitem(nodes.Name(namespace, 'load'),
                            nodes.Const('parent_resource'), 'load')
                    ).set_lineno(lineno),
                    nodes.Assign(
                        nodes.Name(MARKINGS, 'store'),
                        nodes.Name(temp.name, 'load')
                    ).set_lineno(lineno),
        ]

    def _push_resource(self, namespace, site, resource, template, caller):
        """
        Saves the current references in a stack.
        """
        namespace['parent_resource'] = resource
        if not hasattr(resource, 'depends'):
            resource.depends = []
        if not template in resource.depends:
            resource.depends.append(template)
        namespace['resource'] = site.content.resource_from_relative_path(
                                    template)
        return ''

    def _assign_reference(self, markings, namespace, caller):
        """
        Assign the processed variables into the
        given namespace.
        """

        out = caller()
        for key, value in markings.items():
            namespace[key] = value
        namespace['html'] = HtmlWrap(out)
        return ''


class HydeLoader(FileSystemLoader):
    """
    A wrapper around the file system loader that performs
    hyde specific tweaks.
    """

    def __init__(self, sitepath, site, preprocessor=None):
        config = site.config if hasattr(site, 'config') else None
        if config:
            super(HydeLoader, self).__init__([
                            unicode(config.content_root_path),
                            unicode(config.layout_root_path),
                        ])
        else:
            super(HydeLoader, self).__init__(unicode(sitepath))

        self.site = site
        self.preprocessor = preprocessor

    def get_source(self, environment, template):
        """
        Calls the plugins to preprocess prior to returning the source.
        """
        template = template.strip()
        # Fixed so that jinja2 loader does not have issues with
        # seprator in windows
        #
        template = template.replace(os.sep, '/')
        logger.debug("Loading template [%s] and preprocessing" % template)
        (contents,
            filename,
                date) = super(HydeLoader, self).get_source(
                                        environment, template)
        if self.preprocessor:
            resource = self.site.content.resource_from_relative_path(template)
            if resource:
                contents = self.preprocessor(resource, contents) or contents
        return (contents, filename, date)


# pylint: disable-msg=W0104,E0602,W0613,R0201
class Jinja2Template(Template):
    """
    The Jinja2 Template implementation
    """

    def __init__(self, sitepath):
        super(Jinja2Template, self).__init__(sitepath)

    def configure(self, site, engine=None):
        """
        Uses the site object to initialize the jinja environment.
        """
        self.site = site
        self.engine = engine
        self.preprocessor = (engine.preprocessor
                            if hasattr(engine, 'preprocessor') else None)

        self.loader = HydeLoader(self.sitepath, site, self.preprocessor)

        default_extensions = [
                IncludeText,
                Spaceless,
                Asciidoc,
                Markdown,
                restructuredText,
                Syntax,
                Reference,
                Refer,
                YamlVar,
                'jinja2.ext.do',
                'jinja2.ext.loopcontrols',
                'jinja2.ext.with_'
        ]

        defaults = {
            'line_statement_prefix': '$$$',
            'trim_blocks': True,
        }

        settings = dict()
        settings.update(defaults)
        settings['extensions'] = list()
        settings['extensions'].extend(default_extensions)

        conf = {}

        try:
            conf = attrgetter('config.jinja2')(site).to_dict()
        except AttributeError:
            pass

        settings.update(
            dict([(key, conf[key]) for key in defaults if key in conf]))

        extensions = conf.get('extensions', [])
        if isinstance(extensions, list):
            settings['extensions'].extend(extensions)
        else:
            settings['extensions'].append(extensions)

        self.env = Environment(
                    loader=self.loader,
                    undefined=SilentUndefined,
                    line_statement_prefix=settings['line_statement_prefix'],
                    trim_blocks=True,
                    bytecode_cache=FileSystemBytecodeCache(),
                    extensions=settings['extensions'])
        self.env.globals['media_url'] = media_url
        self.env.globals['content_url'] = content_url
        self.env.globals['full_url'] = full_url
        self.env.globals['engine'] = engine
        self.env.globals['deps'] = {}
        self.env.filters['urlencode'] = urlencode
        self.env.filters['urldecode'] = urldecode
        self.env.filters['asciidoc'] = asciidoc
        self.env.filters['markdown'] = markdown
        self.env.filters['restructuredtext'] = restructuredtext
        self.env.filters['syntax'] = syntax
        self.env.filters['date_format'] = date_format
        self.env.filters['xmldatetime'] = xmldatetime
        self.env.filters['islice'] = islice
        self.env.filters['top'] = top

        config = {}
        if hasattr(site, 'config'):
            config = site.config

        self.env.extend(config=config)

        try:
            from typogrify.templatetags import jinja2_filters
        except ImportError:
            jinja2_filters = False

        if jinja2_filters:
            jinja2_filters.register(self.env)

    def clear_caches(self):
        """
        Clear all caches to prepare for regeneration
        """
        if self.env.bytecode_cache:
            self.env.bytecode_cache.clear()


    def get_dependencies(self, path):
        """
        Finds dependencies hierarchically based on the included
        files.
        """
        text = self.env.loader.get_source(self.env, path)[0]
        from jinja2.meta import find_referenced_templates
        try:
            ast = self.env.parse(text)
        except:
            logger.error("Error parsing[%s]" % path)
            raise
        tpls = find_referenced_templates(ast)
        deps = list(self.env.globals['deps'].get('path', []))
        for dep in tpls:
            deps.append(dep)
            if dep:
                deps.extend(self.get_dependencies(dep))
        return list(set(deps))

    @property
    def exception_class(self):
        """
        The exception to throw. Used by plugins.
        """
        return TemplateError

    @property
    def patterns(self):
        """
        The pattern for matching selected template statements.
        """
        return {
           "block_open": '\s*\{\%\s*block\s*([^\s]+)\s*\%\}',
           "block_close": '\s*\{\%\s*endblock\s*([^\s]*)\s*\%\}',
           "include": '\s*\{\%\s*include\s*(?:\'|\")(.+?\.[^.]*)(?:\'|\")\s*\%\}',
           "extends": '\s*\{\%\s*extends\s*(?:\'|\")(.+?\.[^.]*)(?:\'|\")\s*\%\}'
        }

    def get_include_statement(self, path_to_include):
        """
        Returns an include statement for the current template,
        given the path to include.
        """
        return '{%% include \'%s\' %%}' % path_to_include

    def get_extends_statement(self, path_to_extend):
        """
        Returns an extends statement for the current template,
        given the path to extend.
        """
        return '{%% extends \'%s\' %%}' % path_to_extend

    def get_open_tag(self, tag, params):
        """
        Returns an open tag statement.
        """
        return '{%% %s %s %%}' % (tag, params)

    def get_close_tag(self, tag, params):
        """
        Returns an open tag statement.
        """
        return '{%% end%s %%}' % tag

    def get_content_url_statement(self, url):
        """
        Returns the content url statement.
        """
        return '{{ content_url(\'%s\') }}' % url

    def get_media_url_statement(self, url):
        """
        Returns the media url statement.
        """
        return '{{ media_url(\'%s\') }}' % url

    def get_full_url_statement(self, url):
        """
        Returns the full url statement.
        """
        return '{{ full_url(\'%s\') }}' % url

    def render_resource(self, resource, context):
        """
        Renders the given resource using the context
        """
        try:
            template = self.env.get_template(resource.relative_path)
            out = template.render(context)
        except:
            out = ""
            logger.debug(self.env.loader.get_source(
                                self.env, resource.relative_path))
            raise
        return out

    def render(self, text, context):
        """
        Renders the given text using the context
        """
        template = self.env.from_string(text)
        return template.render(context)
