# -*- coding: utf-8 -*-
from __future__ import print_function

import logging
import exhibitionist.settings as settings

def getLogger(name, level=settings.DEFAULT_LOG_LEVEL):
    logger = logging.getLogger(name.replace("exhibitionist.", ""))

    sh = logging.FileHandler(settings.LOG_FILE)
    sh.setFormatter(settings.LOG_FORMAT)
    logger.setLevel(level)


    logger.addHandler(sh)

    return logger