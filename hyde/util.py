"""
Module for python 2.6 compatibility.
"""
import logging
import os
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
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        if sys.platform == 'win32':
            formatter = logging.Formatter(
                            fmt="%(asctime)s %(name)s %(message)s",
                            datefmt='%H:%M:%S')
        else:
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
    if not logger.handlers:
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
        message   = message.replace("$RESET", RESET_SEQ)\
                           .replace("$BOLD",  BOLD_SEQ)\
                           .replace("$COLOR", color)
        for k,v in COLORS.items():
            message = message.replace("$" + k,    COLOR_SEQ % (v+30))\
                             .replace("$BG" + k,  COLOR_SEQ % (v+40))\
                             .replace("$BG-" + k, COLOR_SEQ % (v+40))
        return message + RESET_SEQ

logging.ColorFormatter = ColorFormatter

def make_method(method_name, method_):
    def method__(*args, **kwargs):
        return method_(*args, **kwargs)
    method__.__name__ = method_name
    return method__

def add_property(obj, method_name, method_, *args, **kwargs):
    from functools import partial
    m = make_method(method_name, partial(method_, *args, **kwargs))
    setattr(obj, method_name, property(m))

def add_method(obj, method_name, method_, *args, **kwargs):
    from functools import partial
    m = make_method(method_name, partial(method_, *args, **kwargs))
    setattr(obj, method_name, m)

def pairwalk(iterable):
    a, b = tee(iterable)
    next(b, None)
    return izip(a, b)

def first_match(predicate, iterable):
    """
    Gets the first element matched by the predicate
    in the iterable.
    """
    for item in iterable:
        if predicate(item):
            return item
    return None

def discover_executable(name):
    """
    Finds an executable in the path list provided by the PATH
    environment variable.
    """
    for path in os.environ['PATH'].split(os.pathsep):
        full_name = os.path.join(path, name)
        if os.path.exists(full_name):
            return full_name
    return None