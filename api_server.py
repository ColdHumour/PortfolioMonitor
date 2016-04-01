# -*- coding: utf-8 -*-

"""
api_server.py

porfolio monitor api server

@author: yudi.wu
"""

import os
from flask import Flask, send_from_directory
from flask.ext.restful import Resource, Api

app = Flask("PortfolioMonitor")
api = Api(app)

from lib.positions import Positions
from lib.snapshot import Snapshot
from lib.utils.path import SNAPSHOT_IMG_FILE

hist_pos = Positions()
last_pos = hist_pos._history_positions[hist_pos._trading_days[-1]]
snapshot = Snapshot('000300.XSHG', last_pos)
snapshot.load_data()
if not os.path.isfile(SNAPSHOT_IMG_FILE):
    snapshot.draw_timeline()


class APIServer(Resource):
    def get(self, target):
        snapshot.load_data()
        snapshot.draw_timeline()
        return ""

        # if hasattr(pos, target):
        #     return getattr(pos, target)
        # else:
        #     return ""

    def put(self, target):
        return ""

api.add_resource(APIServer, '/api/<string:target>')


class Home(Resource):
    def get(self):
        return send_from_directory('./static', 'home.html')

api.add_resource(Home, '/', '/home')


if __name__ == '__main__':
    app.run(debug=True)
    # app.run()
