# -*- coding: utf-8 -*-

"""
trading_calendar.py

utility functions for trading days and minutes

@author: yudi.wu
"""

import os
import json
import pandas as pd


MODULE_PATH = os.path.abspath(os.path.dirname(__file__))
RESOURCES_PATH = os.path.join(MODULE_PATH, 'resources')


def get_all_trading_days():
    filedir = os.path.join(RESOURCES_PATH, 'trading_days')
    f = file(filedir).readlines()
    return [row.strip() for row in f]


def get_all_trading_minutes():
    filedir = os.path.join(RESOURCES_PATH, 'trading_minutes')
    f = file(filedir).readlines()
    return [row.strip() for row in f]


if __name__ == "__main__":
    TRADING_DAYS = get_all_trading_days()
    print "Trading Days: from {} to {}".format(TRADING_DAYS[0], TRADING_DAYS[-1])
    
    TRADING_MINUTES = get_all_trading_minutes()
    print "Trading Minutes: from {} to {}".format(TRADING_MINUTES[0], TRADING_MINUTES[-1])
