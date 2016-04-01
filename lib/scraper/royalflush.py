# -*- coding: utf-8 -*-

"""
royalflush.py

market data scraper from 10jqka
"""

import urllib
from bs4 import BeautifulSoup

BASEURL_INDEX = "http://stockpage.10jqka.com.cn/HQ.html#32_399300"
BASEURL_SECURITY = "http://d.10jqka.com.cn/v2/time/hs_600570/last.js"


def complete_url(base, sec):
    """form complete url of specific security for query"""


def parse_snapshot_html(html):
    """parse snapshot contents get from 10jqka finance"""
