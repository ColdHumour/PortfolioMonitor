# -*- coding: utf-8 -*-

"""
data_terminal.py

class Terminal to collect all information and interact with server

@author: yudi.wu
"""

import json
from copy import deepcopy
from datetime import datetime
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter

from positions import Positions
from snapshot import Snapshot

from . scraper.baidu import (
    load_crossectional_close_prices,
    load_daily_close_prices,
)

from . utils.path import CONFIG_FILE, BENCHMARK_FILE, HISTORY_IMG_FILE
from . utils.log import logger
from . utils.trading_calendar import get_trading_days


class Terminal(object):
    def __init__(self):
        self._need_save = False
        self._benchmark = None
        self._benchmark_history = None
        self._benchmark_return = None
        self._portfolio_history = None
        self._portfolio_return = None
        self._trading_days = None

        self._positions = Positions()
        self._auto_fill_positions()
        self._load_benchmark()
        self._draw_history_timeline()
        # self._snapshot = Snapshot(self._benchmark, self._positions)

    def _auto_fill_positions(self):
        today = datetime.now().strftime("%Y-%m-%d")
        trading_days_raw = self._positions._trading_days
        trading_days_new = get_trading_days(trading_days_raw[-1], today)
        if len(trading_days_new) > 1:
            self._need_save = True

        latest_valid_date = trading_days_raw[-1]
        latest_position = self._positions.get_position(latest_valid_date)

        if today == trading_days_new[-1]:
            self._need_save = True
            trading_days_new = trading_days_new[1:-1]
            self._positions.set_current_info(today, latest_position)
        else:
            self._positions.set_current_info(trading_days_new[-1], latest_position)

        self._trading_days = trading_days_raw + trading_days_new

        if trading_days_new:
            logger.info("Filling {} by positions at {}...".format(trading_days_new, latest_valid_date))

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
            logger.info("Filling complete!")

            self._positions.save_all()
            logger.info("Latest history positions information saved.")

        self._portfolio_history = self._positions.history_values
        v0 = self._portfolio_history[0]
        self._portfolio_return = [v/v0 - 1 for v in self._portfolio_history]

    def _load_benchmark(self):
        config = json.load(file(CONFIG_FILE))
        benchmark = config["benchmark"]
        start = self._trading_days[0]
        end = self._trading_days[-1]

        try:
            benchmark_info = json.load(file(BENCHMARK_FILE))
            assert benchmark_info['sec_id'] == benchmark
            assert benchmark_info['start'] == start
            assert benchmark_info['end'] == end
        except:
            logger.info("Benchmark data file is outdated. Downloading new benchmark data...")

            data = load_daily_close_prices(universe=[benchmark],
                                           start=start, end=end)
            assert len(data[benchmark]) == len(self._trading_days)

            logger.info("Downloading complete!")

            benchmark_info = {
                "sec_id": benchmark,
                "start": start,
                "end": end,
                "data": data[benchmark],
            }
            f = open(BENCHMARK_FILE, 'w')
            f.write(json.dumps(benchmark_info, sort_keys=True, indent=4))
            f.close()
            logger.info("Latest benchmark information saved.")

        self._benchmark = benchmark
        self._benchmark_history = benchmark_info['data']
        assert len(self._benchmark_history) == len(self._portfolio_history)
        v0 = self._benchmark_history[0]
        self._benchmark_return = [v/v0 - 1 for v in self._benchmark_history]

    def _draw_history_timeline(self):
        fig = Figure(figsize=(10, 5))
        canvas = FigureCanvas(fig)
        ax_ret = fig.add_subplot(121, axisbg='white')
        ax_val = fig.add_subplot(122, axisbg='white')

        d = len(self._trading_days)
        xseries = range(d)
        xlabels = [t[-5:] for t in self._trading_days]
        pct = lambda x, _: '{0:1.1f}%'.format(100 * x)

        if d > 5:
            tseries = xseries[::d//5+1] + xseries[-1:]
            tlabels = xlabels[::d//5+1] + xlabels[-1:]

        ax_ret.clear()
        ax_ret.plot(xseries, self._portfolio_return, label='portfolio', linewidth=1.0, color='r')
        ax_ret.plot(xseries, self._benchmark_return, label='benchmark', linewidth=1.0, color='b')

        ax_ret.yaxis.set_major_formatter(FuncFormatter(pct))
        ax_ret.set_xlim(0, d-1)
        ax_ret.set_xticks(tseries)
        ax_ret.set_xticklabels(tlabels)
        ax_ret.set_title('Cumulative Return')
        ax_ret.grid(True)
        ax_ret.legend(loc=2, prop={'size': 10})

        # ax.yaxis.set_major_formatter(FuncFormatter(pct))
        # for item in ax.get_yticklabels():
        #     item.set_size(10)

        ax_val.clear()
        ax_val.plot(xseries, self._portfolio_history, label='portfolio', linewidth=1.0, color='r')
        ax_val.set_xlim(0, d-1)
        ax_val.set_xticks(tseries)
        ax_val.set_xticklabels(tlabels)
        ax_val.set_title('Portfolio Value')
        ax_val.grid(True)

        fig.tight_layout()
        fig.savefig(HISTORY_IMG_FILE)

        logger.info("./temp/history.jpg has been saved")
