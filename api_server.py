# -*- coding: utf-8 -*-

"""
api_server.py

porfolio monitor api server

@author: yudi.wu
"""

## TODO
# 1. highchart


from flask import Flask, request, send_from_directory
from flask.ext.restful import Resource, Api

app = Flask("PortfolioMonitor")
api = Api(app)

from lib.terminal import Terminal
from lib.utils.log import logger

terminal = Terminal()


class APIServer(Resource):
    def get(self, api):
        if hasattr(terminal, api):
            return getattr(terminal, api)
        else:
            return ""

    def put(self, api):
        if hasattr(terminal, api):
            getattr(terminal, api)(request.form["pos_string"])
            return ""
        else:
            return ""

api.add_resource(APIServer, '/api/<string:api>')


class Home(Resource):
    def get(self):
        return send_from_directory('./static', 'home.html')

api.add_resource(Home, '/', '/home')


if __name__ == '__main__':
    # app.run(debug=True)
    app.run()
