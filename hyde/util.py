"""
Module for python 2.6 compatibility.
"""
import logging
import sys
from itertools import ifilter, izip, tee

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

def getLoggerWithConsoleHandler(logger_name):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    formatter = ColorFormatter(fmt="$RESET %(asctime)s "
                                      "$BOLD$COLOR%(name)s$RESET "
                                      "%(message)s", datefmt='%H:%M:%S')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def getLoggerWithNullHandler(logger_name):
    """
    Gets the logger initialized with the `logger_name`
    and a NullHandler.
    """
    logger = logging.getLogger(logger_name)
    logger.addHandler(NullHandler())
    return logger


## Code stolen from :
## http://stackoverflow.com/questions/384076/how-can-i-make-the-python-logging-output-to-be-colored/2532931#2532931
##
BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

COLORS = {
    'WARNING'  : YELLOW,
    'INFO'     : WHITE,
    'DEBUG'    : BLUE,
    'CRITICAL' : YELLOW,
    'ERROR'    : RED,
    'RED'      : RED,
    'GREEN'    : GREEN,
    'YELLOW'   : YELLOW,
    'BLUE'     : BLUE,
    'MAGENTA'  : MAGENTA,
    'CYAN'     : CYAN,
    'WHITE'    : WHITE,
}

RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ  = "\033[1m"

class ColorFormatter(logging.Formatter):

    def __init__(self, *args, **kwargs):
        # can't do super(...) here because Formatter is an old school class
        logging.Formatter.__init__(self, *args, **kwargs)

    def format(self, record):
        levelname = record.levelname
        color     = COLOR_SEQ % (30 + COLORS[levelname])
        message   = logging.Formatter.format(self, record)
        if sys.platform == 'win32':
            message = message.replace("$RESET", "")\
                             .replace("$BOLD",  "")\
                             .replace("$COLOR", "")
            for k,v in COLORS.items():
                if sys.platform =='win32':
                    message = message.replace("$" + k,    "")\
                                     .replace("$BG" + k,  "")\
                                     .replace("$BG-" + k, "")
            return message
        else:
            message = message.replace("$RESET", RESET_SEQ)\
                             .replace("$BOLD",  BOLD_SEQ)\
                             .replace("$COLOR", color)
            for k,v in COLORS.items():
                message = message.replace("$" + k,    COLOR_SEQ % (v+30))\
                                 .replace("$BG" + k,  COLOR_SEQ % (v+40))\
                                 .replace("$BG-" + k, COLOR_SEQ % (v+40))
            return message + RESET_SEQ

logging.ColorFormatter = ColorFormatter


def make_method(method_name, method_):
    def method__(self):
        return method_(self)
    method__.__name__ = method_name
    return method__

def add_method(obj, method_name, method_, *args, **kwargs):
    from functools import partial
    m = make_method(method_name, partial(method_, *args, **kwargs))
    setattr(obj, method_name, m)
    
def pairwalk(iterable):
    a, b = tee(iterable)
    next(b, None)
    return izip(a, b)