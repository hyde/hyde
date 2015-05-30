#!/usr/bin/env python
# -*- coding: utf-8 -*-

if __name__ == "__main__":
    import sys
    import warnings

    from hyde.engine import Engine
    
    warnings.filterwarnings('always', category=DeprecationWarning)

    message = ("Running hyde using '{0}' will be deprecated in 1.0. " 
        "Use 'hyde' command instead".format(sys.argv[0]))
    warnings.warn(DeprecationWarning(message), stacklevel=1)

    Engine().run()
