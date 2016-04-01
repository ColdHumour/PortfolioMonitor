# -*- coding: utf-8 -*-

"""
snapshot.py

Class Snapshot to load realtime data of given universe.

@author: yudi.wu
"""

import os
import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter

from scraper.baidu import load_intraday_data
from utils.log import logger
from utils.path import SNAPSHOT_IMG_FILE
from utils.trading_calendar import get_all_trading_minutes

TRADING_MINUTES = get_all_trading_minutes()


class Snapshot(object):
    def __init__(self, benchmark, position):
        self._benchmark = benchmark
        self._position = position
        self._universe = set(position['securities'].keys()) | set([benchmark])

        self._data = None
        self._benchmark_pre_close = None
        self._benchmark_timeline = []
        self._portfolio_pre_close = None
        self._portfolio_timeline = []
        self._last_snapshot = {}

    def load_data(self):
        self._data = load_intraday_data(self._universe)

        self._benchmark_pre_close = self._data[self._benchmark]['pre_close']
        self._benchmark_timeline = self._data[self._benchmark]['timeline']
        d = len(self._benchmark_timeline)

        self._portfolio_pre_close = self._position['cash']
        for sec, secinfo in self._position['securities'].iteritems():
            self._portfolio_pre_close += secinfo['amount'] * self._data[sec]['pre_close']
            secinfo['price'] = self._data[sec]['timeline'][-1]

        self._portfolio_timeline = []
        for i in range(d):
            v = self._position['cash']
            for sec, secinfo in self._position['securities'].iteritems():
                v += secinfo['amount'] * self._data[sec]['timeline'][i]
            self._portfolio_timeline.append(v)
        self._position['value'] = v

        self._benchmark_timeline = [v / self._benchmark_pre_close - 1 for v in self._benchmark_timeline]
        self._portfolio_timeline = [v / self._portfolio_pre_close - 1 for v in self._portfolio_timeline]

        self._benchmark_timeline += [np.nan] * (241 - d)
        self._portfolio_timeline += [np.nan] * (241 - d)

    def draw_timeline(self):
        fig = Figure(figsize=(8, 4))
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111, axisbg='white')

        xseries = range(len(TRADING_MINUTES))
        pct = lambda x, _: '{0:1.1f}%'.format(100*x)
        xseries_show = xseries[::30]
        xlabels_show = TRADING_MINUTES[::30]

        ax.clear()
        ax.plot(xseries, self._portfolio_timeline, label='portfolio', linewidth=1.0, color='r')
        ax.plot(xseries, self._benchmark_timeline, label='benchmark', linewidth=1.0, color='b')

        ax.yaxis.set_major_formatter(FuncFormatter(pct))
        for item in ax.get_yticklabels():
            item.set_size(10)

        ax.set_xlim(0, 240)
        ax.set_xticks(xseries_show)
        ax.set_xticklabels(xlabels_show, fontsize=10)

        ax.grid(True)
        ax.legend(loc=2, prop={'size': 12})

        fig.savefig(SNAPSHOT_IMG_FILE)

        logger.info("./temp/snapshot.jpg has been saved")

    def latest_snapshot(self):
        pass

    def latest_position(self):
        return self._position
