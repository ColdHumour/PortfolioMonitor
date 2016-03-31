# -*- coding: utf-8 -*-

"""
data_terminal.py

class Terminal to collect all information and interact with server

@author: yudi.wu
"""

import os
import json
from datetime import datetime

from positions import Positions
from snapshot import Snapshot

MODULE_PATH = os.path.abspath(os.path.dirname(__file__))
CONFIG_FILE = os.path.join(MODULE_PATH, 'config.json')


class Terminal(object):
    def __init__(self):
        today = datetime.now().strftime("%Y-%m-%d")

        config = json.load(file(CONFIG_FILE))
        self._benchmark = config["benchmark"]
        self._positions = Positions()

        # date


        self._snapshot = Snapshot(self._benchmark, self._positions)

    def _load_benchmark(self):
        pass
