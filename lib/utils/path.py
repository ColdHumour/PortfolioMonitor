# -*- coding: utf-8 -*-

"""
path.py

Generate all absolute paths the module used.

@author: yudi.wu
"""

import os


MODULE_PATH = os.path.dirname(__file__)
MODULE_PATH = os.path.dirname(MODULE_PATH)
MODULE_PATH = os.path.dirname(MODULE_PATH)
MODULE_PATH = os.path.abspath(MODULE_PATH)

LIB_PATH = os.path.join(MODULE_PATH, "lib")
STATIC_FILES_PATH = os.path.join(MODULE_PATH, "static")

CONFIG_FILE = os.path.join(MODULE_PATH, "config.json")

POSITION_DB_PATH = os.path.join(LIB_PATH, "posdb")
RESOURCES_PATH = os.path.join(LIB_PATH, "resources")

BENCHMARK_FILE = os.path.join(STATIC_FILES_PATH, 'temp', 'benchmark.json')
LOG_FILE = os.path.join(STATIC_FILES_PATH, 'temp', 'server.log')
SNAPSHOT_IMG_FILE = os.path.join(STATIC_FILES_PATH, 'temp', 'snapshot.jpg')
HISTORY_IMG_FILE = os.path.join(STATIC_FILES_PATH, 'temp', 'history.jpg')
