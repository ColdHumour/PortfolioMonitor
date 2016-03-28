# -*- coding: utf-8 -*-

"""
positions.py

positions class use info in posdb, storing data in json format

@author: yudi.wu
"""

import os
import json
import pandas as pd


MODULE_PATH = os.path.abspath(os.path.dirname(__file__))
POSITION_DB_PATH = os.path.join(MODULE_PATH, 'posdb')


class Positions(object):
    """class to trace all positions"""

    def __init__(self):
        self._trading_days = []
        self._history_positions = {}
        self._current_date = None
        self._current_position = {}

        self._load_positions()

    def _load_positions(self):
        """load history positions and trading days from database"""

        jsonlist = os.listdir(POSITION_DB_PATH)
        for month_json in jsonlist:
            month_pos = json.load(file(os.path.join(POSITION_DB_PATH, month_json)))
            self._history_positions.update(month_pos)
        self._trading_days = sorted(self._history_positions)

    def set_current_info(self, date, position):
        self._current_date = date
        self._current_position = position

    def save_current_position(self):
        if self._current_date not in self._history_positions:
            self._history_positions[self._current_date] = self._current_position
            self._trading_days.append(self._current_date)

            month = self._current_date[:7]
            month_json = "{}.json".format(month)
            month_pos = {date: self._history_positions[k] for date in self._trading_days if date[:7] == month}
            f = open(os.path.join(POSITION_DB_PATH, month_json), 'w')
            f.write(json.dumps(month_pos, sort_keys=True, indent=4))
            f.close()

    def save_all(self):
        if self._current_date is not None and self._current_date not in self._history_positions:
            self._history_positions[self._current_date] = self._current_position
            self._trading_days.append(self._current_date)

        jsonlist = set([date[:7] for date in self._trading_days])
        for month in jsonlist:
            month_json = "{}.json".format(month)
            month_pos = {date: self._history_positions[date] for date in self._trading_days if date[:7] == month}
            f = open(os.path.join(POSITION_DB_PATH, month_json), 'w')
            f.write(json.dumps(month_pos, sort_keys=True, indent=4))
            f.close()


if __name__ == "__main__":
    pos = Positions()
