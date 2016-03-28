# -*- coding: utf-8 -*- 

import sys

from PyQt4 import QtCore, QtGui
from matplotlib import pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

from styles import *
from data_parse import *


class GroupBox(QtGui.QGroupBox):
    def __init__(self, title=''):
        super(GroupBox, self).__init__()
        self.setTitle(title)
        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)
    
    def addWidget(self, widget, *args, **kwargs):
        self.layout.addWidget(widget, *args, **kwargs)
    
    def addItem(self, item, *args, **kwargs):
        self.layout.addItem(item, *args, **kwargs)
    
    def addLayout(self, layout, *args, **kwargs):
        self.layout.addLayout(layout, *args, **kwargs)


class PortfolioMonitor(QtGui.QWidget):
    def __init__(self):
        super(PortfolioMonitor, self).__init__()
        self.loadWidgets()
        self.loadLayout()
                
    def loadWidgets(self):
        get_current_position()
        
        fig_history = plt.figure()
        self.canvas_history = FigureCanvas(fig_history)
        self.ax_history_ret = fig_history.add_subplot(121, axisbg='white')
        self.ax_history_val = fig_history.add_subplot(122, axisbg='white')
        plt.subplots_adjust(top=0.9, bottom=0.1, left=0.1, right=0.95, wspace=0.3)
        self.draw_history()

        self.grb_snapshot = GroupBox()
        self.label_time = QtGui.QLabel()
        self.label_pinfo = QtGui.QLabel()
        self.label_binfo = QtGui.QLabel()
        self.refresh_btn = QtGui.QPushButton('refresh')
        self.connect(self.refresh_btn, QtCore.SIGNAL('clicked()'), self.load_snapshot)
        
        self.grb_pdetails = GroupBox('Portfolio Details')
        self.label_title = QtGui.QLabel(u'      证券代码   证券简称  持有数量  当前价格  当日收益  总体涨跌')
        cash, secpos = get_current_position()
        self.seclist = secpos.keys()
        self.secidxmap = {sec:i for i,sec in enumerate(self.seclist)}
        self.seclabels = [QtGui.QLabel() for sec in self.seclist]
        
        fig_snapshot = plt.figure()
        self.canvas_snapshot = FigureCanvas(fig_snapshot)
        self.ax_snapshot = fig_snapshot.add_subplot(111, axisbg='white')
        self.load_snapshot()

    def loadLayout(self):
        self.setWindowTitle('Private Portfolio Monitor')
        self.resize(750, 780+len(self.seclist)*30)
        self.canvas_snapshot.setFixedHeight(350)
        self.canvas_history.setFixedHeight(300)
        
        self.grb_snapshot.setFixedHeight(100)
        self.grb_snapshot.setStyleSheet("border:0")
        self.refresh_btn.setFixedWidth(200)
        self.refresh_btn.setStyleSheet(btn_style)
        
        self.grb_snapshot.addWidget(self.label_time, 0, 0, 1, 1)
        self.grb_snapshot.addWidget(self.refresh_btn, 0, 1, 1, 1)
        self.grb_snapshot.addWidget(self.label_pinfo, 1, 0, 1, -1)
        self.grb_snapshot.addWidget(self.label_binfo, 2, 0, 1, -1)
        
        self.grb_pdetails.setFixedHeight(100 if len(self.seclist) < 3 else 30+len(self.seclist)*30)
        self.grb_pdetails.setFont(QtGui.QFont('Consolas', 12))
        self.grb_pdetails.addWidget(self.label_title, 0, 0, 1, 1)
        self.label_title.setStyleSheet(title_style)
        for i,label in enumerate(self.seclabels):
            self.grb_pdetails.addWidget(label, i+1, 0, 1, 1)
    
        layout = QtGui.QGridLayout()
        layout.addWidget(self.grb_snapshot, 0, 0, 1, -1)
        layout.addWidget(self.canvas_snapshot, 1, 0, 1, -1)
        layout.addWidget(self.grb_pdetails, 2, 0, 1, -1)
        layout.addWidget(self.canvas_history, 3, 0, 1, -1)
        
        self.setLayout(layout)
    
    def load_snapshot(self):
        values, series, shots = get_snapshot(get_current_position(), self.baseinfo)
        self.set_snapshot_labels(values)
        self.draw_snapshot(series)
        self.set_portfolio_details(shots)
    
    def set_snapshot_labels(self, values_necessary):
        cur_t, ini_v, cur_v, ini_b, cur_b = values_necessary
        
        self.label_time.setText('Time: {0}'.format(cur_t))
        self.label_time.setFont(QtGui.QFont('Consolas', 15, QtGui.QFont.Bold))
        
        pinfo = 'Portfolio: {0:8.2f}  {1:7.2f}  {2:5.2f}%'.format(cur_v, cur_v-ini_v, 100.*(cur_v/ini_v-1))
        self.label_pinfo.setText(pinfo)
        if cur_v-ini_v >= 0:
            self.label_pinfo.setStyleSheet(profit_style_ptf)
        else:
            self.label_pinfo.setStyleSheet(loss_style_ptf)
        
        binfo = 'Benchmark: {0:8.2f}  {1:7.2f}  {2:5.2f}%'.format(cur_b, cur_b-ini_b, 100.*(cur_b/ini_b-1))
        self.label_binfo.setText(binfo)
        if cur_b-ini_b >= 0:
            self.label_binfo.setStyleSheet(profit_style_ptf)
        else:
            self.label_binfo.setStyleSheet(loss_style_ptf)
        
    def set_portfolio_details(self, prices_necessary):
        secname, secpos, ltcpshot, clspshot = prices_necessary
        for sec,am in secpos.items():
            i = self.secidxmap[sec]
            sinfo = u'    {0}  {1} {2:7.0f} {3:10.2f} {4:8.2f}% {5:9.2f}' \
                   .format(sec, secname[sec] + u'　'*(4-len(secname[sec])), am, clspshot[sec], 
                           100.*(clspshot[sec]/ltcpshot[sec]-1),
                           am*(clspshot[sec]-ltcpshot[sec]))
            self.seclabels[i].setText(sinfo)
            if clspshot[sec]-ltcpshot[sec] >= 0:
                self.seclabels[i].setStyleSheet(profit_style_sec)
            else:
                self.seclabels[i].setStyleSheet(loss_style_sec)
    
    def draw_snapshot(self, series_necessary):
        barTime, aseries, bseries = series_necessary
        xseries = range(len(barTime))
        pct = lambda x,_: '{0:1.1f}%'.format(100*x)
        xseries_show = xseries[::24]
        xlabels_show = barTime[::24]
        
        self.ax_snapshot.clear()
        self.ax_snapshot.plot(xseries, aseries, label='portfolio', linewidth=1.0, color='r')
        self.ax_snapshot.plot(xseries, bseries, label='benchmark', linewidth=1.0, color='b')
        
        self.ax_snapshot.yaxis.set_major_formatter(FuncFormatter(pct))
        self.ax_snapshot.set_xlim(0, len(barTime)-1)
        self.ax_snapshot.set_xticks(xseries_show)
        self.ax_snapshot.set_xticklabels(xlabels_show)
        self.ax_snapshot.grid(True)
        self.ax_snapshot.legend(loc=2, prop={'size':10})
        
        self.canvas_snapshot.draw()
    
    def draw_history(self):
        self.baseinfo, (tradingdays, vseries, aseries, bseries) = get_historyline(get_history_position())
        xseries = range(len(tradingdays))
        xlabels = [t[-4:] for t in tradingdays]
        pct = lambda x,_: '{0:1.1f}%'.format(100*x)
        
        self.ax_history_ret.clear()
        self.ax_history_ret.plot(xseries, aseries, label='portfolio', linewidth=1.0, color='r')
        self.ax_history_ret.plot(xseries, bseries, label='benchmark', linewidth=1.0, color='b')

        if len(xseries) > 5:
            tseries = xseries[::len(xseries)/5+1]
            tlabels = xlabels[::len(xseries)/5+1]
        
        self.ax_history_ret.yaxis.set_major_formatter(FuncFormatter(pct))
        self.ax_history_ret.set_xlim(0, len(xseries)-1)
        self.ax_history_ret.set_xticks(tseries)
        self.ax_history_ret.set_xticklabels(tlabels)
        self.ax_history_ret.set_title('Cumulative Return')
        self.ax_history_ret.grid(True)
        self.ax_history_ret.legend(loc=2, prop={'size':10})
        
        self.ax_history_val.clear()
        self.ax_history_val.plot(xseries, vseries, label='portfolio', linewidth=1.0, color='r')
        self.ax_history_val.set_xlim(0, len(xseries)-1)
        self.ax_history_val.set_xticks(tseries)
        self.ax_history_val.set_xticklabels(tlabels)
        self.ax_history_val.set_title('Portfolio Value')
        self.ax_history_val.grid(True)
        
        self.canvas_history.draw()
    

if __name__ == '__main__':
    app = QtGui.QApplication.instance() 
    if not app: app = QtGui.QApplication(sys.argv)

    window = PortfolioMonitor()
    window.show()
    sys.exit(app.exec_())