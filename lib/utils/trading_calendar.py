# -*- coding: utf-8 -*-

"""
trading_calendar.py

utility functions for trading days and minutes

@author: yudi.wu
"""

import os
from datetime import datetime
from . path import RESOURCES_PATH


def get_all_trading_days():
    filedir = os.path.join(RESOURCES_PATH, 'trading_days')
    with open(filedir, 'r') as file_info:
        f = file_info.readlines()
    return [row.strip() for row in f]

TRADING_DAYS_ALL = get_all_trading_days()
TRADING_DAYS_DICT = {date: i for i, date in enumerate(TRADING_DAYS_ALL)}


def get_trading_days(start, end):
    """all trading days between start and end (including both ends)"""

    try:
        datetime.strptime(start, "%Y-%m-%d")
    except:
        raise ValueError("Invalid format: {}".format(start))

    try:
        datetime.strptime(end, "%Y-%m-%d")
    except:
        raise ValueError("Invalid format: {}".format(end))

    trading_days = [date for date in TRADING_DAYS_ALL if start <= date <= end]
    return trading_days


def get_trading_days_relatively(start, n):
    """all trading days based on start and moving direction"""

    try:
        datetime.strptime(start, "%Y-%m-%d")
    except:
        raise ValueError("Invalid format: {}".format(start))

    if start not in TRADING_DAYS_ALL:
        start = max(date for date in TRADING_DAYS_ALL if date <= start)

    i_start = TRADING_DAYS_DICT[start]
    i_end = i_start + n
    if i_start < i_end:
        return TRADING_DAYS_ALL[i_start:i_end+1]
    else:
        return TRADING_DAYS_ALL[i_end:i_start+1]


def get_all_trading_minutes():
    filedir = os.path.join(RESOURCES_PATH, 'trading_minutes')
    with open(filedir, 'r') as file_info:
        f = file_info.readlines()
    return [row.strip() for row in f]

TRADING_MINUTES = get_all_trading_minutes()
