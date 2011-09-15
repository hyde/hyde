#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2011, lepture.com
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above
#      copyright notice, this list of conditions and the following
#      disclaimer in the documentation and/or other materials provided
#      with the distribution.
#    * Neither the name of the author nor the names of its contributors
#      may be used to endorse or promote products derived from this
#      software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT 
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from hyde.plugin import CLTransformer
from hyde.fs import File

from operator import attrgetter


class SuffixPlugin(CLTransformer):
    """
    The plugin class for suffix modified
    """

    def __init__(self, site):
        super(SuffixPlugin, self).__init__(site)

    def begin_site(self):
        """
        Configuration example
        ---------------------
        #yaml
        suffix:
            -
                target_extension:
                    - markdown
                    - md
                output_extension: html
            -
                target_extension:
                    - rst
                    - md
                output_extension: html
        """
        config = self.site.config
        if not hasattr(config, 'suffix'):
            return

        suffix_config = attrgetter('suffix')(config)

        for resource in self.site.content.walk_resources():
            for conf in suffix_config:
                conf = conf.to_dict()
                target = conf.get('target_extension', [])
                output = conf.get('output_extension', 'html')
                if resource.source_file.kind in target:
                    new_name = resource.source_file.name_without_extension + "." + output
                    target_folder = File(resource.relative_deploy_path).parent
                    resource.relative_deploy_path = target_folder.child(new_name)


    @property
    def plugin_name(self):
        """
        The name of the plugin.
        """
        return "suffix"
