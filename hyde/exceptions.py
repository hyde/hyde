class HydeException(Exception):
    """Base class for exceptions from hyde."""

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None
    def __repr__(self):
        """What is printed if something goes wrong"""
        if self.message:
            return "Exception raised: {}".format(self.message)
        else:
            return "Unlucky there bud"