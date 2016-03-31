# -*- coding: utf-8 -*-

"""
trading_calendar.py

utility functions for trading days and minutes

@author: yudi.wu
"""

import os
from datetime import datetime


MODULE_PATH = os.path.abspath(os.path.dirname(__file__))
RESOURCES_PATH = os.path.join(MODULE_PATH, 'resources')


def get_all_trading_days():
    filedir = os.path.join(RESOURCES_PATH, 'trading_days')
    f = file(filedir).readlines()
    return [row.strip() for row in f]


def get_trading_days(start, end):
    try:
        datetime.strptime(start, "%Y-%m-%d")
    except:
        raise ValueError("Invalid format: {}".format(start))

    try:
        datetime.strptime(end, "%Y-%m-%d")
    except:
        raise ValueError("Invalid format: {}".format(end))

    trading_days_all = get_all_trading_days()
    trading_days = [date for date in trading_days_all if start <= date <= end]
    return trading_days


def get_all_trading_minutes():
    filedir = os.path.join(RESOURCES_PATH, 'trading_minutes')
    f = file(filedir).readlines()
    return [row.strip() for row in f]


if __name__ == "__main__":
    TRADING_DAYS = get_all_trading_days()
    print "Trading Days: from {} to {}".format(TRADING_DAYS[0], TRADING_DAYS[-1])

    TRADING_MINUTES = get_all_trading_minutes()
    print "Trading Minutes: from {} to {}".format(TRADING_MINUTES[0], TRADING_MINUTES[-1])
