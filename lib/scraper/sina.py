# -*- coding: utf-8 -*-

"""
sina.py

market data scraper from sina

function list:
    load_sec_shortname
"""

import json
import re
from urllib import urlopen

from gevent import monkey
from gevent.pool import Pool
monkey.patch_socket()

from .. utils.log import logger
from .. utils.path import CONFIG_FILE


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

    logger.debug("get \"{}\"".format(url))

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

    logger.info("Loading shortnames of {}...".format(universe))

    def load_sec(sec):
        url = complete_url(sec_id_mapping(sec))
        data = parse_url_for_shortname(url)
        return sec, data

    config = json.load(file(CONFIG_FILE))
    concurrent = config["concurrent"]
    pool = Pool(concurrent)
    requests = [pool.spawn(load_sec, sec) for sec in universe]
    pool.join()

    data_all = {}
    for response in requests:
        sec, data = response.value
        data[sec] = data
    return data_all
