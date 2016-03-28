# -*- coding: utf-8 -*-

"""
baidu.py

market data scraper from baidu
"""


import datetime
import json
from urllib import urlopen
# from bs4 import BeautifulSoup

from .. trading_calendar import get_all_trading_minutes
TRADING_MINUTES = get_all_trading_minutes()


# 当日所有分钟线数据，应该是从ticker计算出来的，有缺失
BASEURL_INTRADAY = "http://gupiao.baidu.com/api/stocks/stocktimeline?from=pc&os_ver=1&cuid=xxx&vv=100&format=json&stock_code={sec_id}"

# 从该股票某个交易日往前数若干天（包含当日）的日线数据，如果停牌则跳过
BASEURL_DAILY = "http://gupiao.baidu.com/api/stocks/stockdaybar?from=pc&os_ver=1&cuid=xxx&vv=100&format=json&stock_code={sec_id}&start={date}&count={bar_amount}&fq_type=no"


def sec_id_mapping(sec_id):
    """map standard sec_id to the form baidu url uses"""

    if sec_id.endswith('.XSHG'):
        return 'sh' + sec_id[:6]
    else:
        return 'sz' + sec_id[:6]


def complete_intraday_url(sec_id):
    return BASEURL_INTRADAY.format(sec_id=sec_id)


def complete_daily_url(date, n, sec_id):
    """daily data of sec_id: n tradings days before date (include date)"""

    return BASEURL_DAILY.format(date=date, bar_amount=n, sec_id=sec_id)


def date_mapping(date):
    """map date from baidu url to standard form"""

    return '{}-{}-{}'.format(date // 10000, (date % 10000) // 100, date % 100)


def time_mapping(time):
    """map time (minute bar) from baidu url to standard form"""

    time //= 100000
    hour, minute = divmod(time, 100)

    if hour < 10:
        hour = '0' + str(hour)
    else:
        hour = str(hour)

    if minute < 10:
        minute = '0' + str(minute)
    else:
        minute = str(minute)

    return '{}:{}'.format(hour, minute)


def parse_url_for_intraday_data(url):
    try:
        html = urlopen(url)
    except:
        raise ValueError("Cannot open {}".format(url))

    try:
        info = json.load(html)
    except:
        raise ValueError("Wrond data format at {}".format(url))

    market_data_raw = {time_mapping(snapshot['time']): snapshot['price'] for snapshot in info['timeLine']}

    open_minute = [m for m in market_data_raw if m <= "09:30"]
    if not open_minute:
        raise ValueError("Open minute missing!")
    else:
        open_minute = open_minute[-1]

    now = datetime.datetime.now()
    last_minute = now.strftime("%H:%M")
    if now.second < 30:
        trading_minutes = [m for m in TRADING_MINUTES if m < last_minute]
    else:
        trading_minutes = [m for m in TRADING_MINUTES if m <= last_minute]

    for i, m in enumerate(trading_minutes):
        if m not in market_data_raw:
            if i == 0:
                market_data_raw[m] = market_data_raw[open_minute]
            else:
                market_data_raw[m] = market_data_raw[trading_minutes[i-1]]

    market_data = [market_data_raw[m] for m in trading_minutes]
    return market_data


def load_intraday_data(universe):
    """all sec_ids in universe are in standard form"""

    data = {}
    for sec in universe:
        url = complete_intraday_url(sec_id_mapping(sec))
        data[sec] = parse_url_for_intraday_data(url)
    return data
