# -*- coding: utf-8 -*-

"""
sina.py

market data scraper from sina
"""

import urllib
from bs4 import BeautifulSoup

BASEURL_SNAPSHOT = "http://hq.sinajs.cn/list="


def complete_url(base, sec):
    """form complete url of specific security for query"""


def parse_snapshot_html(html):
    """parse snapshot contents get from sina finance"""
