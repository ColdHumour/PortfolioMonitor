# -*- coding: utf-8 -*-

"""
log.py

@author: yudi.wu
"""

import json
import logging
from . path import LOG_FILE, CONFIG_FILE
open(LOG_FILE, 'w').close()


def set_logger(name, level):
    logger = logging.Logger(name)
    logger.setLevel(level)

    # set handler
    handler = logging.FileHandler(LOG_FILE)
    handler.setLevel(level)

    # set formatter
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] File:%(filename)s Line:%(lineno)d - %(message)s')
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    return logger


with open(CONFIG_FILE, 'r') as config_file:
    config = json.load(config_file)
loglevel = config["loglevel"]
logger = set_logger("APIServer", getattr(logging, loglevel))
