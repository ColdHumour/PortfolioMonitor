# -*- coding: utf-8 -*-

"""
api_server.py

porfolio monitor api server

@author: yudi.wu
"""

## TODO
# 1. put request
# 2. setinterval
# 3. gevent


from flask import Flask, send_from_directory
from flask.ext.restful import Resource, Api

app = Flask("PortfolioMonitor")
api = Api(app)

from lib.terminal import Terminal
from lib.utils.log import logger

terminal = Terminal()


class APIServer(Resource):
    def get(self, target):
        if hasattr(terminal, target):
            return getattr(terminal, target)
        else:
            return ""

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
