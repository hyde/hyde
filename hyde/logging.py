"""
Module for python 2.6 compatibility.
"""
import logging

try:
    from logging import NullHandler
except:
    class NullHandler(logging.Handler):
        """
        NOOP handler for libraries.
        """
        def emit(self, record):
            """
            /dev/null
            """
            pass

def getLoggerWithNullHandler(logger_name):
    """
    Gets the logger initialized with the `logger_name`
    and a NullHandler.
    """
    logger = logging.getLogger(logger_name)
    logger.addHandler(NullHandler())
