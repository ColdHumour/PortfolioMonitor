# -*- coding: utf-8 -*-

"""
data_terminal.py

class Terminal to collect all information and interact with server

@author: yudi.wu
"""

import os
import json
from copy import deepcopy
from datetime import datetime
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter

from . positions import Positions
from . snapshot import Snapshot

from . scraper.sina import load_sec_shortname
from . scraper.baidu import (
    load_crossectional_close_prices,
    load_daily_close_prices,
)

from . utils.log import logger
from . utils.path import CONFIG_FILE, BENCHMARK_CACHE_FILE, HISTORY_IMG_FILE
from . utils.trading_calendar import (
    get_trading_days,
    get_trading_days_relatively,
    TRADING_DAYS_DICT,
)


class Terminal(object):
    """
    用于和前端交互的数据终端，可用于交互的方法和属性有：
    - update_position(pos_string): 接收前端的持仓字符串，刷新position和snapshot，仅在交易日09:30-15:00有效
    - save(): 保存最新的仓位，仅在交易日15:00后有效
    - reload_snapshot: 刷新snapshot，返回刷新后的overall_info和detail_info
    - snapshot_overall_info: 最新的overall_info
    - snapshot_detail_info: 最新的detail_info
    - latest_position_string: 最新的position的简单字符串形式，以供修改
    """

    def __init__(self):
        self._benchmark = None
        self._benchmark_history = None
        self._benchmark_return = None
        self._portfolio_history = None
        self._portfolio_return = None
        self._trading_days = None

        self._positions = Positions()
        self._auto_fill_positions()
        self._load_benchmark()
        if not os.path.isfile(HISTORY_IMG_FILE):
            self._draw_history_timeline()

        self._snapshot = Snapshot(self._benchmark, self._positions.get_current_position())

    def _auto_fill_positions(self):
        now = datetime.now()
        today = now.strftime("%Y-%m-%d")
        yesterday = get_trading_days_relatively(today, -1)[0]

        trading_days_raw = self._positions._trading_days
        latest_valid_date = trading_days_raw[-1]
        latest_position = self._positions.get_position(latest_valid_date)

        trading_days_new = get_trading_days(latest_valid_date, yesterday)[1:]
        self._trading_days = trading_days_raw + trading_days_new
        if today in TRADING_DAYS_DICT:
            self._positions.set_current_info(today, deepcopy(latest_position))
        else:
            self._positions.set_current_info(yesterday, deepcopy(latest_position))

        if trading_days_new:
            logger.info("Filling positions data of {} through scraper, referring position at {}...".format(trading_days_new, latest_valid_date))

            for date in trading_days_new:
                temp_pos = deepcopy(latest_position)
                universe = temp_pos['securities'].keys()
                data = load_crossectional_close_prices(universe, date)

                value = temp_pos['cash']
                for sec, p in data.iteritems():
                    temp_pos['securities'][sec]['price'] = p
                    value += p * temp_pos['securities'][sec]['amount']
                temp_pos['value'] = value
                self._positions.set_info(date, temp_pos, is_new_date=True)
            logger.info("Successfully filled positions data!")

            self._positions.save_all()
            logger.info("Latest positions data saved at /lib/posdb/.")

        self._portfolio_history = self._positions.history_values
        v0 = self._portfolio_history[0]
        self._portfolio_return = [v/v0 - 1 for v in self._portfolio_history]

    def _load_benchmark(self):
        logger.info("Loading benchmark data file...")

        with open(CONFIG_FILE, 'r') as config_file:
            config = json.load(config_file)
        benchmark = config["benchmark"]
        start = self._trading_days[0]
        end = self._trading_days[-1]
        redraw = False

        try:
            with open(BENCHMARK_CACHE_FILE, 'r') as bm_file:
                benchmark_info = json.load(bm_file)
            assert benchmark_info['sec_id'] == benchmark
            assert benchmark_info['start'] == start
            assert benchmark_info['end'] == end
            logger.info("Successfully loaded benchmark data file!")
        except:
            redraw = True
            logger.info("Benchmark data file is outdated. Downloading benchmark data ({}) from {} to {} through scraper...".format(benchmark, start, end))

            data = load_daily_close_prices(universe=[benchmark],
                                           start=start, end=end)
            assert len(data[benchmark]) == len(self._trading_days)
            logger.info("Successfully downloaded benchmark data!")

            benchmark_info = {
                "sec_id": benchmark,
                "start": start,
                "end": end,
                "data": data[benchmark],
            }
            f = open(BENCHMARK_CACHE_FILE, 'w')
            f.write(json.dumps(benchmark_info, sort_keys=True, indent=4))
            f.close()
            logger.info("Benchmark data saved at ./static/temp/benchmark.json.")

        self._benchmark = benchmark
        self._benchmark_history = benchmark_info['data']
        assert len(self._benchmark_history) == len(self._portfolio_history)
        v0 = self._benchmark_history[0]
        self._benchmark_return = [v/v0 - 1 for v in self._benchmark_history]
        if redraw:
            self._draw_history_timeline()

    def _draw_history_timeline(self):
        fig = Figure(figsize=(7, 3))
        canvas = FigureCanvas(fig)
        ax_ret = fig.add_subplot(121, axisbg='white')
        ax_val = fig.add_subplot(122, axisbg='white')

        d = len(self._trading_days)
        xseries = list(range(d))
        xlabels = [t[-5:] for t in self._trading_days]
        pct = lambda x, _: '{0:1.1f}%'.format(100 * x)

        if d > 5:
            tseries = xseries[::d//5+1] + xseries[-1:]
            tlabels = xlabels[::d//5+1] + xlabels[-1:]

        # draw return lines
        ax_ret.clear()
        ax_ret.plot(xseries, self._portfolio_return, label='portfolio', linewidth=1.0, color='r')
        ax_ret.plot(xseries, self._benchmark_return, label='benchmark', linewidth=1.0, color='b')

        ax_ret.yaxis.set_major_formatter(FuncFormatter(pct))
        for item in ax_ret.get_yticklabels():
            item.set_size(9)
        ax_ret.set_xlim(0, d-1)
        ax_ret.set_xticks(tseries)
        ax_ret.set_xticklabels(tlabels, fontsize=9)
        ax_ret.set_title('Cumulative Return', fontsize=10)
        ax_ret.grid(True)
        ax_ret.legend(loc=2, prop={'size': 8})

        # draw value line
        ax_val.clear()
        ax_val.plot(xseries, self._portfolio_history, label='portfolio', linewidth=1.0, color='r')

        for item in ax_val.get_yticklabels():
            item.set_size(9)
        ax_val.set_xlim(0, d-1)
        ax_val.set_xticks(tseries)
        ax_val.set_xticklabels(tlabels, fontsize=9)
        ax_val.set_title('Portfolio Value', fontsize=10)
        ax_val.grid(True)

        fig.tight_layout()
        fig.savefig(HISTORY_IMG_FILE)
        logger.info("History image saved at ./static/temp/history.")

    def update_position(self, pos_string):
        new_position = self._parse_new_pos_string(pos_string)

        now = datetime.now()
        today = now.strftime("%Y-%m-%d")
        minute = now.strftime("%H:%M")
        if today in TRADING_DAYS_DICT and "09:30" <= minute <= "15:00":
            self._snapshot.update_position(new_position)
            self._positions.set_current_info(today, self._snapshot.latest_position())

    def _parse_new_pos_string(self, pos_string):
        pos_info = [r.strip() for r in pos_string.strip().split("\n")]
        pos_dict = {}
        pos_dict["cash"] = float(pos_info[0])
        pos_dict["securities"] = {}
        pos_dict["value"] = 0.0

        for r in pos_info[1:]:
            sec, amount = r.split("|")
            sec += ".XSHG" if sec[0] == "6" else ".XSHE"
            pos_dict["securities"][sec] = {
                "amount": float(amount),
                "price": 0.0,
                "name": None,
            }

        short_names = load_sec_shortname(pos_dict["securities"].keys())
        for sec, name in short_names.items():
            pos_dict["securities"][sec]["name"] = name
        return pos_dict

    @property
    def save(self):
        now = datetime.now()
        today = now.strftime("%Y-%m-%d")
        minute = now.strftime("%H:%M")
        if today in TRADING_DAYS_DICT and minute > "15:00":
            self._snapshot.save()
            self._positions.set_current_info(today, self._snapshot.latest_position())
            self._positions.save_current_position()
        return ""

    @property
    def reload_snapshot(self):
        now = datetime.now()
        self._today = now.strftime("%Y-%m-%d")
        self._yesterday = get_trading_days_relatively(self._today, -1)
        self._minute = now.strftime("%H:%M")
        self._is_trading_day = self._today in TRADING_DAYS_DICT

        self._snapshot.refresh()
        return {
            "snapshot_overall_info": self.snapshot_overall_info,
            "snapshot_detail_info": self.snapshot_detail_info
        }

    @property
    def snapshot_overall_info(self):
        return self._snapshot.latest_overall_info_in_html()

    @property
    def snapshot_detail_info(self):
        return self._snapshot.latest_securities_details_in_html()

    @property
    def latest_position_string(self):
        return self._snapshot.latest_position_in_simple_string()
