"""
The generator class and related utility functions.
"""

class Generator(object):
    """
    Generates output from a node or resource.
    """

    def __init__(self, site):
        super(Generator, self).__init__()
        self.site = site

    def generate_all(self):
        """
        Generates the entire website
        """
        pass

    def generate_node(self, node=None):
        """
        Generates a single node. If node is non-existent or empty
        generates the entire site.
        """
        pass

    def generate_resource(self, resource=None):
        """
        Generates a single resource. If resource is non-existent or empty
        generats the entire website.
        """
        pass


