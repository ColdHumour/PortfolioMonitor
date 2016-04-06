# -*- coding: utf-8 -*-

"""
snapshot.py

Class Snapshot to load realtime data of given universe.

@author: yudi.wu
"""

import json
import numpy as np
from copy import deepcopy
from datetime import datetime
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter

from scraper.baidu import load_latest_intraday_close_prices
from utils.log import logger
from utils.path import SNAPSHOT_CACHE_FILE, SNAPSHOT_IMG_FILE
from utils.trading_calendar import (
    get_trading_days_relatively,
    TRADING_DAYS_DICT,
    TRADING_MINUTES,
)


class Snapshot(object):
    def __init__(self, benchmark, position):
        self._benchmark = benchmark
        self._position = deepcopy(position)
        self._universe = set(position["securities"].keys()) | set([benchmark])

        self._today = None
        self._yesterday = None
        self._is_trading_day = None
        self._last_minute = None

        self._benchmark_last_value = None
        self._benchmark_pre_close = None
        self._benchmark_timeline = []
        self._portfolio_last_value = None
        self._portfolio_pre_close = None
        self._portfolio_timeline = []
        self._pre_close = None

        self.refresh()

    def refresh(self):
        now = datetime.now()
        self._today = now.strftime("%Y-%m-%d")
        self._yesterday = get_trading_days_relatively(self._today, -1)
        self._is_trading_day = self._today in TRADING_DAYS_DICT
        self._last_minute = now.strftime("%H:%M")
        if self._is_trading_day:
            if self._last_minute < "09:30":
                self._last_minute = "15:00"
            elif "11:30" < self._last_minute < "13:00":
                self._last_minute = "11:30"
            elif self._last_minute > "15:00":
                self._last_minute = "15:00"
        else:
            self._last_minute = "15:00"

        try:
            self._load_data_from_cache()
            logger.info("Successfully loaded snapshot cache...")
        except:
            self.load_data_from_scraper()
            self.draw_timeline()
            if self._last_minute < "09:30" or \
               "11:30" <= self._last_minute < "13:00" or \
               self._last_minute >= "15:00":
                self.save()

    def load_data_from_cache(self):
        logger.info("Loading snapshot data cache...")
        data = json.load(file(SNAPSHOT_CACHE_FILE))
        if self._is_trading_day:
            if self._last_minute < "09:30":
                assert data["date"] == self._yesterday
                assert data["minute"] == "15:00"
            else:
                assert data["date"] == self._today
                assert data["minute"] == self._last_minute
        else:
            assert data["date"] == self._yesterday
            assert data["minute"] == "15:00"

        assert data["benchmark"] == self._benchmark
        assert data["position"]["cash"] == self._position["cash"]
        assert sorted(data["position"]["securities"].keys()) == sorted(self._position["securities"].keys())

        self._benchmark_last_value = data["benchmark_last_value"]
        self._benchmark_pre_close = data["benchmark_pre_close"]
        self._portfolio_last_value = data["portfolio_last_value"]
        self._portfolio_pre_close = data["portfolio_pre_close"]
        self._pre_close = data["pre_close"]

    def load_data_from_scraper(self):
        logger.info("Downloading snapshot data through scraper...")

        data = load_latest_intraday_close_prices(self._universe, self._is_trading_day)
        logger.info("Successfully downloaded snapshot data!")

        self._pre_close = {sec: data[sec]["pre_close"] for sec in self._position["securities"]}
        self._benchmark_pre_close = data[self._benchmark]["pre_close"]
        self._benchmark_timeline = data[self._benchmark]["timeline"]
        self._benchmark_last_value = self._benchmark_timeline[-1]
        d = len(self._benchmark_timeline)

        self._portfolio_pre_close = self._position["cash"]
        for sec, secinfo in self._position["securities"].iteritems():
            self._portfolio_pre_close += secinfo["amount"] * self._pre_close[sec]
            secinfo["price"] = data[sec]["timeline"][-1]

        self._portfolio_timeline = []
        for i in range(d):
            v = self._position["cash"]
            for sec, secinfo in self._position["securities"].iteritems():
                v += secinfo["amount"] * data[sec]["timeline"][i]
            self._portfolio_timeline.append(v)
        self._position["value"] = v
        self._portfolio_last_value = v

        self._benchmark_timeline = [v / self._benchmark_pre_close - 1 for v in self._benchmark_timeline]
        self._portfolio_timeline = [v / self._portfolio_pre_close - 1 for v in self._portfolio_timeline]

        self._benchmark_timeline += [np.nan] * (241 - d)
        self._portfolio_timeline += [np.nan] * (241 - d)

    def draw_timeline(self):
        fig = Figure(figsize=(7, 3))
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111, axisbg="white")

        xseries = range(len(TRADING_MINUTES))
        pct = lambda x, _: "{0:1.1f}%".format(100*x)
        xseries_show = xseries[::30]
        xlabels_show = TRADING_MINUTES[::30]

        ax.clear()
        ax.plot(xseries, self._portfolio_timeline, label="portfolio", linewidth=1.0, color="r")
        ax.plot(xseries, self._benchmark_timeline, label="benchmark", linewidth=1.0, color="b")

        ax.yaxis.set_major_formatter(FuncFormatter(pct))
        for item in ax.get_yticklabels():
            item.set_size(10)

        ax.set_xlim(0, 240)
        ax.set_xticks(xseries_show)
        ax.set_xticklabels(xlabels_show, fontsize=10)

        ax.grid(True)
        ax.legend(loc=2, prop={"size": 9})

        fig.tight_layout()
        fig.savefig(SNAPSHOT_IMG_FILE)
        logger.info("Snapshot image saved at ./static/temp/snapshot.jpg.")

    def save(self):
        snapshot_info = {
            "date": self._today,
            "minute": self._last_minute,
            "benchmark": self._benchmark,
            "pre_close": self._pre_close,
            "position": self._position,
            "benchmark_last_value": self._benchmark_last_value,
            "benchmark_pre_close": self._benchmark_pre_close,
            "portfolio_last_value": self._portfolio_last_value,
            "portfolio_pre_close": self._portfolio_pre_close,
        }

        f = open(SNAPSHOT_CACHE_FILE, "w")
        f.write(json.dumps(snapshot_info, sort_keys=True, indent=4))
        f.close()
        logger.info("Snapshot data saved at ./static/temp/snapshot.json.")

    def update_position(self, new_position):
        if self._is_trading_day and "09:30" <= self._last_minute <= "15:00":
            self._position = new_position
            self._universe = set(new_position["securities"].keys()) | set([self._benchmark])
            self.load_data_from_scraper()
            self.draw_timeline()

    def latest_position(self):
        return self._position

    def latest_position_in_simple_string(self):
        pos_string = "{:.2f}\n".format(self._position["cash"])
        for sec in sorted(self._position["securities"]):
            pos_string += "{}|{}\n".format(sec[:6], int(self._position["securities"][sec]["amount"]))
        return pos_string

    def latest_overall_info_in_html(self):
        info_html = "<table id=\"overall\">"
        info_html += "<tr><td class=\"item\">Time:</td><td class=\"value\">{}</td><td></td><td></td></tr>".format(self._last_minute)

        portfolio_ret = (self._portfolio_last_value / self._portfolio_pre_close) * 100 - 100
        flag = "profit" if portfolio_ret >= 0 else "loss"
        info_html += "<tr class=\"{}\"><td class=\"item\">Portfolio:</td><td class=\"price\">{:.2f}</td><td class=\"price\">{:.2f}</td><td class=\"price\">{:.2f}%</td></tr>".format(
            flag,
            round(self._portfolio_last_value, 2),
            round(self._portfolio_last_value - self._portfolio_pre_close, 2),
            round(portfolio_ret, 2))

        benchmark_ret = (self._benchmark_last_value / self._benchmark_pre_close) * 100 - 100
        flag = "profit" if benchmark_ret >= 0 else "loss"
        info_html += "<tr class=\"{}\"><td class=\"item\">Benchmark:</td><td class=\"price\">{:.2f}</td><td class=\"price\">{:.2f}</td><td class=\"price\">{:.2f}%</td></tr>".format(
            flag,
            round(self._benchmark_last_value, 2),
            round(self._benchmark_last_value - self._benchmark_pre_close, 2),
            round(benchmark_ret, 2))
        info_html += "</table>"
        return info_html

    def latest_securities_details_in_html(self):
        table_html = u"<table id=\"detail\">"

        head = [u"证券代码", u"证券简称", u"持有数量", u"当前价格", u"当日收益", u"总体涨跌"]
        table_html += u"<tr><th class=\"name\">{}</th><th class=\"name\">{}</th><th class=\"price\">{}</th><th class=\"price\">{}</th><th class=\"price\">{}</th><th class=\"price\">{}</th></tr>".format(*head)

        for sec in sorted(self._position["securities"]):
            info = self._position["securities"][sec]
            pre_close = self._pre_close[sec]
            ret = (info["price"] / pre_close - 1)*100
            flag = "profit" if ret >= 0 else "loss"
            row = [flag,
                   sec[:6],
                   info["name"],
                   str(int(info["amount"])),
                   "{:.2f}".format(round(info["price"], 2)),
                   "{:.2f}%".format(round(ret, 2)),
                   "{:.2f}".format(round((info["price"] - pre_close) * info["amount"], 2))]
            table_html += u"<tr class=\"{}\"><td class=\"name\">{}</td><td class=\"name\">{}</td><td class=\"price\">{}</td><td class=\"price\">{}</td><td class=\"price\">{}</td><td class=\"price\">{}</td></tr>".format(*row)

        table_html += "</table>"
        return table_html
