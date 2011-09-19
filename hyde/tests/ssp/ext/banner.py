from hyde.plugin import Plugin


class BannerPlugin(Plugin):
	"""
	Adds a comment banner to all generated html files
	"""

	def text_resource_complete(self, resource, text):
		banner = """
<!--
This file was produced with infinite love, care & sweat.
Please dont copy. If you have to, please drop me a note.
-->
"""
		if resource.source.kind == "html":
			text = banner + text
		return text