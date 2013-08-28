# -*- coding: utf-8 -*-
"""
Use nose
`$ pip install nose`
`$ nosetests`
"""

from hyde.generator import Generator
from hyde.plugin import Plugin
from hyde.site import Site
from hyde.model import Expando

from mock import patch, Mock

from fswrap import File, Folder

TEST_SITE = File(__file__).parent.child_folder('_test')

class PluginLoaderStub(Plugin):
    pass

class NoReturnPlugin(Plugin):

    def begin_text_resource(self, resource, text):
        print "NoReturnPlugin"
        return None

class ConstantReturnPlugin(Plugin):

    def begin_text_resource(self, resource, text):
        print "ConstantReturnPlugin"
        return "Jam"


class TestPlugins(object):

    @classmethod
    def setup_class(cls):
        TEST_SITE.make()
        TEST_SITE.parent.child_folder('sites/test_jinja').copy_contents_to(TEST_SITE)
        folders = []
        text_files = []
        binary_files = []

        with TEST_SITE.child_folder('content').walker as walker:
            @walker.folder_visitor
            def visit_folder(folder):
                folders.append(folder.path)

            @walker.file_visitor
            def visit_file(afile):
                if not afile.is_text:
                    binary_files.append(afile.path)
                else:
                    text_files.append(afile.path)

        cls.content_nodes = sorted(folders)
        cls.content_text_resources = sorted(text_files)
        cls.content_binary_resources = sorted(binary_files)


    @classmethod
    def teardown_class(cls):
        TEST_SITE.delete()

    def setUp(self):
         self.site = Site(TEST_SITE)
         self.site.config.plugins = ['hyde.tests.test_plugin.PluginLoaderStub']

    def test_can_load_plugin_modules(self):
        assert not len(self.site.plugins)
        Plugin.load_all(self.site)

        assert len(self.site.plugins) == 1
        assert self.site.plugins[0].__class__.__name__ == 'PluginLoaderStub'


    def test_generator_loads_plugins(self):
        gen = Generator(self.site)
        assert len(self.site.plugins) == 1

    def test_generator_template_registered_called(self):
        with patch.object(PluginLoaderStub, 'template_loaded') as template_loaded_stub:
            gen = Generator(self.site)
            gen.generate_all()
            assert template_loaded_stub.call_count == 1

    def test_generator_template_begin_generation_called(self):
        with patch.object(PluginLoaderStub, 'begin_generation') as begin_generation_stub:
            gen = Generator(self.site)
            gen.generate_all()
            assert begin_generation_stub.call_count == 1

    def test_generator_template_begin_generation_called_for_single_resource(self):
        with patch.object(PluginLoaderStub, 'begin_generation') as begin_generation_stub:
            gen = Generator(self.site)
            path = self.site.content.source_folder.child('about.html')
            gen.generate_resource_at_path(path)

            assert begin_generation_stub.call_count == 1

    def test_generator_template_begin_generation_called_for_single_node(self):
        with patch.object(PluginLoaderStub, 'begin_generation') as begin_generation_stub:
            gen = Generator(self.site)
            path = self.site.content.source_folder
            gen.generate_node_at_path(path)
            assert begin_generation_stub.call_count == 1


    def test_generator_template_generation_complete_called(self):
        with patch.object(PluginLoaderStub, 'generation_complete') as generation_complete_stub:
            gen = Generator(self.site)
            gen.generate_all()
            assert generation_complete_stub.call_count == 1

    def test_generator_template_generation_complete_called_for_single_resource(self):
        with patch.object(PluginLoaderStub, 'generation_complete') as generation_complete_stub:
            gen = Generator(self.site)
            path = self.site.content.source_folder.child('about.html')
            gen.generate_resource_at_path(path)

            assert generation_complete_stub.call_count == 1

    def test_generator_template_generation_complete_called_for_single_node(self):
        with patch.object(PluginLoaderStub, 'generation_complete') as generation_complete_stub:
            gen = Generator(self.site)
            path = self.site.content.source_folder
            gen.generate_node_at_path(path)
            assert generation_complete_stub.call_count == 1

    def test_generator_template_begin_site_called(self):
        with patch.object(PluginLoaderStub, 'begin_site') as begin_site_stub:
            gen = Generator(self.site)
            gen.generate_all()
            assert begin_site_stub.call_count == 1

    def test_generator_template_begin_site_called_for_single_resource(self):
        with patch.object(PluginLoaderStub, 'begin_site') as begin_site_stub:
            gen = Generator(self.site)
            path = self.site.content.source_folder.child('about.html')
            gen.generate_resource_at_path(path)
            assert begin_site_stub.call_count == 1

    def test_generator_template_begin_site_not_called_for_single_resource_second_time(self):
        with patch.object(PluginLoaderStub, 'begin_site') as begin_site_stub:
            gen = Generator(self.site)
            gen.generate_all()
            assert begin_site_stub.call_count == 1
            path = self.site.content.source_folder.child('about.html')
            gen.generate_resource_at_path(path)
            assert begin_site_stub.call_count == 1

    def test_generator_template_begin_site_called_for_single_node(self):
        with patch.object(PluginLoaderStub, 'begin_site') as begin_site_stub:
            gen = Generator(self.site)
            path = self.site.content.source_folder
            gen.generate_node_at_path(path)

            assert begin_site_stub.call_count == 1

    def test_generator_template_begin_site_not_called_for_single_node_second_time(self):
        with patch.object(PluginLoaderStub, 'begin_site') as begin_site_stub:
            gen = Generator(self.site)
            gen.generate_all()
            assert begin_site_stub.call_count == 1
            path = self.site.content.source_folder
            gen.generate_node_at_path(path)

            assert begin_site_stub.call_count == 1

    def test_generator_template_site_complete_called(self):
        with patch.object(PluginLoaderStub, 'site_complete') as site_complete_stub:
            gen = Generator(self.site)
            gen.generate_all()
            assert site_complete_stub.call_count == 1


    def test_generator_template_site_complete_called_for_single_resource(self):

        with patch.object(PluginLoaderStub, 'site_complete') as site_complete_stub:
            gen = Generator(self.site)
            path = self.site.content.source_folder.child('about.html')
            gen.generate_resource_at_path(path)

            assert site_complete_stub.call_count == 1

    def test_generator_template_site_complete_not_called_for_single_resource_second_time(self):

        with patch.object(PluginLoaderStub, 'site_complete') as site_complete_stub:
            gen = Generator(self.site)
            gen.generate_all()
            assert site_complete_stub.call_count == 1
            path = self.site.content.source_folder.child('about.html')
            gen.generate_resource_at_path(path)

            assert site_complete_stub.call_count == 1

    def test_generator_template_site_complete_called_for_single_node(self):

        with patch.object(PluginLoaderStub, 'site_complete') as site_complete_stub:
            gen = Generator(self.site)
            path = self.site.content.source_folder
            gen.generate_node_at_path(path)

            assert site_complete_stub.call_count == 1

    def test_generator_template_site_complete_not_called_for_single_node_second_time(self):

        with patch.object(PluginLoaderStub, 'site_complete') as site_complete_stub:
            gen = Generator(self.site)
            gen.generate_all()
            path = self.site.content.source_folder
            gen.generate_node_at_path(path)

            assert site_complete_stub.call_count == 1

    def test_generator_template_begin_node_called(self):

        with patch.object(PluginLoaderStub, 'begin_node') as begin_node_stub:
            gen = Generator(self.site)
            gen.generate_all()

            assert begin_node_stub.call_count == len(self.content_nodes)
            called_with_nodes = sorted([arg[0][0].path for arg in begin_node_stub.call_args_list])
            assert called_with_nodes == self.content_nodes

    def test_generator_template_begin_node_called_for_single_resource(self):

        with patch.object(PluginLoaderStub, 'begin_node') as begin_node_stub:
            gen = Generator(self.site)
            gen.generate_resource_at_path(self.site.content.source_folder.child('about.html'))
            assert begin_node_stub.call_count == len(self.content_nodes)


    def test_generator_template_begin_node_not_called_for_single_resource_second_time(self):

        with patch.object(PluginLoaderStub, 'begin_node') as begin_node_stub:
            gen = Generator(self.site)
            gen.generate_all()
            assert begin_node_stub.call_count == len(self.content_nodes)
            gen.generate_resource_at_path(self.site.content.source_folder.child('about.html'))
            assert begin_node_stub.call_count == len(self.content_nodes) # No extra calls


    def test_generator_template_node_complete_called(self):

        with patch.object(PluginLoaderStub, 'node_complete') as node_complete_stub:
            gen = Generator(self.site)
            gen.generate_all()

            assert node_complete_stub.call_count == len(self.content_nodes)
            called_with_nodes = sorted([arg[0][0].path for arg in node_complete_stub.call_args_list])
            assert called_with_nodes == self.content_nodes

    def test_generator_template_node_complete_called_for_single_resource(self):

        with patch.object(PluginLoaderStub, 'node_complete') as node_complete_stub:
            gen = Generator(self.site)
            gen.generate_resource_at_path(self.site.content.source_folder.child('about.html'))
            assert node_complete_stub.call_count == len(self.content_nodes)

    def test_generator_template_node_complete_not_called_for_single_resource_second_time(self):

        with patch.object(PluginLoaderStub, 'node_complete') as node_complete_stub:
            gen = Generator(self.site)
            gen.generate_all()
            assert node_complete_stub.call_count == len(self.content_nodes)
            gen.generate_resource_at_path(self.site.content.source_folder.child('about.html'))
            assert node_complete_stub.call_count == len(self.content_nodes) # No extra calls

    def test_generator_template_begin_text_resource_called(self):

        with patch.object(PluginLoaderStub, 'begin_text_resource') as begin_text_resource_stub:
            begin_text_resource_stub.reset_mock()
            begin_text_resource_stub.return_value = ''
            gen = Generator(self.site)
            gen.generate_all()

            called_with_resources = sorted([arg[0][0].path for arg in begin_text_resource_stub.call_args_list])
            assert set(called_with_resources) == set(self.content_text_resources)

    def test_generator_template_begin_text_resource_called_for_single_resource(self):

        with patch.object(PluginLoaderStub, 'begin_text_resource') as begin_text_resource_stub:
            begin_text_resource_stub.return_value = ''
            gen = Generator(self.site)
            gen.generate_all()
            begin_text_resource_stub.reset_mock()
            path = self.site.content.source_folder.child('about.html')
            gen = Generator(self.site)
            gen.generate_resource_at_path(path, incremental=True)

            called_with_resources = sorted([arg[0][0].path for arg in begin_text_resource_stub.call_args_list])
            assert begin_text_resource_stub.call_count == 1
            assert called_with_resources[0] == path

    def test_generator_template_begin_binary_resource_called(self):

        with patch.object(PluginLoaderStub, 'begin_binary_resource') as begin_binary_resource_stub:
            gen = Generator(self.site)
            gen.generate_all()

            called_with_resources = sorted([arg[0][0].path for arg in begin_binary_resource_stub.call_args_list])
            assert begin_binary_resource_stub.call_count == len(self.content_binary_resources)
            assert called_with_resources == self.content_binary_resources

    def test_generator_template_begin_binary_resource_called_for_single_resource(self):

        with patch.object(PluginLoaderStub, 'begin_binary_resource') as begin_binary_resource_stub:
            gen = Generator(self.site)
            gen.generate_all()
            begin_binary_resource_stub.reset_mock()
            path = self.site.content.source_folder.child('favicon.ico')
            gen.generate_resource_at_path(path)

            called_with_resources = sorted([arg[0][0].path for arg in begin_binary_resource_stub.call_args_list])
            assert begin_binary_resource_stub.call_count == 1
            assert called_with_resources[0] == path

    def test_plugin_chaining(self):
         self.site.config.plugins = [
            'hyde.tests.test_plugin.ConstantReturnPlugin',
            'hyde.tests.test_plugin.NoReturnPlugin'
         ]
         path = self.site.content.source_folder.child('about.html')
         gen = Generator(self.site)
         gen.generate_resource_at_path(path)
         about = File(Folder(
                    self.site.config.deploy_root_path).child('about.html'))
         assert about.read_all() == "Jam"

    def test_plugin_filters_begin_text_resource(self):
        def empty_return(self, resource, text=''):
            return text
        with patch.object(ConstantReturnPlugin, 'begin_text_resource', new=Mock(wraps=empty_return)) as mock1:
            with patch.object(NoReturnPlugin, 'begin_text_resource', new=Mock(wraps=empty_return)) as mock2:
                self.site.config.plugins = [
                    'hyde.tests.test_plugin.ConstantReturnPlugin',
                    'hyde.tests.test_plugin.NoReturnPlugin'
                 ]
                self.site.config.constantreturn = Expando(dict(include_file_pattern="*.css"))
                self.site.config.noreturn = Expando(dict(include_file_pattern=["*.html", "*.txt"]))
                gen = Generator(self.site)
                gen.generate_all()
                mock1_args = sorted(set([arg[0][0].name for arg in mock1.call_args_list]))
                mock2_args = sorted(set([arg[0][0].name for arg in mock2.call_args_list]))
                assert len(mock1_args) == 1
                assert len(mock2_args) == 4
                assert mock1_args == ["site.css"]
                assert mock2_args == ["404.html", "about.html", "merry-christmas.html", "robots.txt"]

    def test_plugin_node_filters_begin_text_resource(self):
        def empty_return(*args, **kwargs):
            return None
        with patch.object(ConstantReturnPlugin, 'begin_text_resource', new=Mock(wraps=empty_return)) as mock1:
            with patch.object(NoReturnPlugin, 'begin_text_resource', new=Mock(wraps=empty_return)) as mock2:
                self.site.config.plugins = [
                    'hyde.tests.test_plugin.ConstantReturnPlugin',
                    'hyde.tests.test_plugin.NoReturnPlugin'
                 ]
                self.site.config.constantreturn = Expando(dict(include_paths="media"))
                self.site.config.noreturn = Expando(dict(include_file_pattern="*.html", include_paths=["blog"]))
                gen = Generator(self.site)
                gen.generate_all()
                mock1_args = sorted(set([arg[0][0].name for arg in mock1.call_args_list]))
                mock2_args = sorted(set([arg[0][0].name for arg in mock2.call_args_list]))
                assert len(mock1_args) == 1
                assert len(mock2_args) == 1
                assert mock1_args == ["site.css"]
                assert mock2_args == ["merry-christmas.html"]