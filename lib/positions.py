# -*- coding: utf-8 -*-

"""
positions.py

Class Positions loads info in posdb, which stores data in json format.

@author: yudi.wu
"""

import os
import json
import pandas as pd

from utils.log import logger
from utils.path import POSITION_DB_PATH


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

        logger.info("Loading positions information from posdb...")

        jsonlist = os.listdir(POSITION_DB_PATH)
        for month_json in jsonlist:
            month_pos = json.load(file(os.path.join(POSITION_DB_PATH, month_json)))
            self._history_positions.update(month_pos)
        self._trading_days = sorted(self._history_positions)

        logger.info("Successfully loaded positions information!")

    def get_position(self, date):
        return self._history_positions.get(date, {})

    def get_current_position(self):
        return self._current_position

    def set_info(self, date, position, is_new_date=True):
        self._history_positions[date] = position
        if is_new_date:
            self._trading_days = sorted(self._history_positions)

    def set_current_info(self, date, position):
        self._current_date = date
        self._current_position = position

    def save_current_position(self):
        self._history_positions[self._current_date] = self._current_position
        if self._current_date != self._trading_days[-1]:
            self._trading_days.append(self._current_date)

        month = self._current_date[:7]
        month_json = "{}.json".format(month)
        month_pos = {date: self._history_positions[date] for date in self._trading_days if date[:7] == month}
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

    @property
    def history_values(self):
        return [self._history_positions[date]['value'] for date in self._trading_days]


if __name__ == "__main__":
    pos = Positions()
