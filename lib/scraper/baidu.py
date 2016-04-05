# -*- coding: utf-8 -*-

"""
baidu.py

market data scraper from baidu

function list:
    load_latest_intraday_close_prices
    load_daily_close_prices
    load_crossectional_close_prices
"""


import datetime
import json
import logging
from urllib import urlopen

from .. utils.log import logger
from .. utils.trading_calendar import (
    TRADING_DAYS_ALL,
    TRADING_DAYS_DICT,
    TRADING_MINUTES,
    get_trading_days,
)


# 当日所有分钟线数据，应该是从ticker计算出来的，有缺失
BASEURL_INTRADAY = "http://gupiao.baidu.com/api/stocks/stocktimeline?from=pc&os_ver=1&cuid=xxx&vv=100&format=json&stock_code={sec_id}"

# 从该股票某个交易日往前数若干天（不包含当日）的日线数据，如果停牌则跳过
BASEURL_DAILY = "http://gupiao.baidu.com/api/stocks/stockdaybar?from=pc&os_ver=1&cuid=xxx&vv=100&format=json&stock_code={sec_id}&start={date}&count={bar_amount}&fq_type={fq_type}"


def sec_id_mapping(sec_id):
    """map standard sec_id to the form baidu url uses"""

    if sec_id.endswith('.XSHG'):
        return 'sh' + sec_id[:6]
    else:
        return 'sz' + sec_id[:6]


def complete_intraday_url(sec_id):
    return BASEURL_INTRADAY.format(sec_id=sec_id)


def complete_daily_url(sec_id, date='', n=1, fq_type='no'):
    """
    daily data of sec_id: n tradings days before date (include date)
    sec_id: vis sec_id_mapping
    date: 'YYYY-MM-DD', default current date
    n: integer
    fq_type: ['no', 'front', 'back']
    """

    return BASEURL_DAILY.format(sec_id=sec_id, date=date, bar_amount=n, fq_type=fq_type)


def date_mapping(date):
    """map date from baidu url to standard form"""

    year, date = divmod(date, 10000)
    month, date = divmod(date, 100)

    if month < 10:
        month = '0' + str(month)
    else:
        month = str(month)

    if date < 10:
        date = '0' + str(date)
    else:
        date = str(date)

    return '{}-{}-{}'.format(year, month, date)


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
    """return preClose and timeline"""

    logger.debug("GET \"{}\"".format(url))

    try:
        html = urlopen(url)
    except:
        raise ValueError("Cannot open {}".format(url))

    try:
        info = json.load(html)
    except:
        raise ValueError("Wrong data format at {}".format(url))

    pre_close = info["preClose"]
    timeline = {time_mapping(snapshot['time']): snapshot['price'] for snapshot in info['timeLine']}

    return {'pre_close': pre_close, 'timeline': timeline}


def parse_url_for_daily_close_prices(url):
    """return daily close price series"""

    logger.debug("GET \"{}\"".format(url))

    try:
        html = urlopen(url)
    except:
        raise ValueError("Cannot open {}".format(url))

    try:
        info = json.load(html)
    except:
        raise ValueError("Wrong data format at {}".format(url))

    timeline = {date_mapping(snapshot['date']): snapshot['kline']['close'] for snapshot in info['mashData']}
    return {"close_price": timeline}


def load_latest_intraday_close_prices(universe, is_trading_day=True):
    """all sec_ids in universe are in standard form"""

    logger.info("Loading lastest intraday close prices of {}...".format(universe))

    if is_trading_day:
        now = datetime.datetime.now()
        last_minute = now.strftime("%H:%M")
        if now.second < 30:
            trading_minutes = [m for m in TRADING_MINUTES if m < last_minute]
        else:
            trading_minutes = [m for m in TRADING_MINUTES if m <= last_minute]
    else:
        trading_minutes = TRADING_MINUTES

    data_all = {}
    for sec in universe:
        url = complete_intraday_url(sec_id_mapping(sec))
        data = parse_url_for_intraday_data(url)
        timeline_raw = data['timeline']

        if is_trading_day:
            open_minute = [m for m in timeline_raw if m <= "09:30"]
            if not open_minute:
                raise ValueError("Open minute missing!")
            else:
                open_minute = open_minute[-1]
        else:
            open_minute = "09:30"

        for i, m in enumerate(trading_minutes):
            if m not in timeline_raw:
                if i == 0:
                    timeline_raw[m] = timeline_raw[open_minute]
                else:
                    timeline_raw[m] = timeline_raw[trading_minutes[i-1]]

        data['timeline'] = [timeline_raw[m] for m in trading_minutes]
        data_all[sec] = data
    return data_all


def load_daily_close_prices(universe, start, end):
    """load daily history data for single security"""

    logger.info("Loading daily close prices of {} from {} to {}...".format(universe, start, end))

    trading_days = get_trading_days(start, end)
    n = len(trading_days)

    i_end = TRADING_DAYS_DICT[end]
    end = TRADING_DAYS_ALL[i_end+1]

    if n > 500:
        raise ValueError("Too many trading days between {} and {}!".format(start, end))

    data_all = {}
    for sec in universe:
        url = complete_daily_url(sec_id=sec_id_mapping(sec),
                                 date=end.replace('-', ''),
                                 n=n)
        data = parse_url_for_daily_close_prices(url)
        timeline_raw = data["close_price"]

        for i, date in enumerate(trading_days):
            if date not in timeline_raw:
                timeline_raw[date] = timeline_raw[trading_days[i-1]]

        data["close_price"] = [timeline_raw[date] for date in trading_days]
        data_all[sec] = data["close_price"]
    return data_all


def load_crossectional_close_prices(universe, date):
    """load daily history data for single security"""

    logger.info("Loading crossectional close prices of {} at {}...".format(universe, date))

    if date not in TRADING_DAYS_DICT:
        raise ValueError("{} is not in trading days!".format(date))

    i_date = TRADING_DAYS_DICT[date]
    date = TRADING_DAYS_ALL[i_date+1]

    data_all = {}
    for sec in universe:
        url = complete_daily_url(sec_id=sec_id_mapping(sec),
                                 date=date.replace('-', ''),
                                 n=1)
        data = parse_url_for_daily_close_prices(url)
        data_all[sec] = data["close_price"].values()[0]
    return data_all
