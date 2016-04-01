# -*- coding: utf-8 -*-

"""
sina.py

market data scraper from sina

function list:
    load_sec_shortname
"""

import re
from urllib import urlopen

from .. utils.log import logger


# 当前最新的成交信息
BASEURL_SNAPSHOT = "http://hq.sinajs.cn/list={sec_id}"


def sec_id_mapping(sec_id):
    """map standard sec_id to the form baidu url uses"""

    if sec_id.endswith('.XSHG'):
        return 'sh' + sec_id[:6]
    else:
        return 'sz' + sec_id[:6]


def complete_url(sec_id):
    return BASEURL_SNAPSHOT.format(sec_id=sec_id)


def parse_url_for_shortname(url):
    """return preClose and timeline"""

    try:
        html = urlopen(url)
    except:
        raise ValueError("Cannot open {}".format(url))

    try:
        info = html.read().decode("gbk")
    except:
        raise ValueError("Wrong data format at {}".format(url))

    pattern = re.compile(r'"(.*?)"')
    info = pattern.findall(info)[0]
    info = info.split(",")[0]
    return info


def load_sec_shortname(universe):
    """all sec_ids in universe are in standard form"""

    data = {}
    for sec in universe:
        url = complete_url(sec_id_mapping(sec))
        data[sec] = parse_url_for_shortname(url)
    return data
