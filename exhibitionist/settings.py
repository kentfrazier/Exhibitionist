# -*- coding: utf-8 -*-
from __future__ import print_function

import os
import logging

LOG_FORMAT = logging.Formatter(fmt='%(asctime)s {%(name)-4s: %(lineno)d} %(levelname)-8s  %(message)s', datefmt='%m-%d %H:%M:%S')

make_path = lambda base, suffix: os.path.abspath(os.path.join(base, suffix))

# detect null device on this box
try:
    # *nix
    NULLDEV = "/dev/null"
    with open(NULLDEV, "wb"):
        pass
except:
    # windows: http://stackoverflow.com/questions/313111
    NULLDEV = "NUL"

BASE_DIR = make_path(os.path.dirname(__file__), "..")
# unless a port is specified, the server loops through
# [SERVER_PORT_BASE,SERVER_PORT_BASE+MAX_N_SOCKETS)
# and binds to the first available socket.
SERVER_PORT_BASE = 9080
MAX_N_SOCKETS = 100

# For Exhibitionist only.If None, the package loggers will be NullLogger
DEFAULT_LOG_LEVEL = logging.CRITICAL+1
LOG_FILE = NULLDEV # by default, log to /dev/null

# tornado <=2.4.1 uses the root logger so we can't silence it
# without potentially affecting user code. It's also chatty by default
# which can flood the console with crappy favicon 404 reports.
# So, pipe everything to the platform /dev/null.
# hope this works off-linux.
TORNADO_LOG_FILE = NULLDEV # send the tornado logging to /dev/null

# put these in your local_settings.py to enable
# logging for development
# LOG_FILE=make_path(BASE_DIR,"xb.log")
# TORNADO_LOG_FILE=make_path(BASE_DIR,"tornado.log")
# DEFAULT_LOG_LEVEL=logging.DEBUG


try:
    from local_settings import *
except:# pragma: no cover
    pass
