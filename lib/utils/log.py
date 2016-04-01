# -*- coding: utf-8 -*-

"""
log.py

@author: yudi.wu
"""

import os
import logging
import logging.handlers
from . path import LOG_FILE


logger = logging.Logger("APIServer")
logger.setLevel(logging.INFO)

# set handler
handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=2048, backupCount=0)
handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s [%(levelname)s] File:%(filename)s Line:%(lineno)d - %(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)
