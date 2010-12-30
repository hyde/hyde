"""
Hyde utilities
"""
import sys


def load_python_object(name):
    """
    Loads a python module from string
    """
    (module_name, _ , object_name) = name.rpartition(".")
    __import__(module_name)
    module = sys.modules[module_name]
    return getattr(module, object_name)
