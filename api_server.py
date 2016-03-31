# -*- coding: utf-8 -*-

"""
api_server.py

porfolio monitor api server

@author: yudi.wu
"""


from flask import Flask, request
from flask.ext.restful import Resource, Api

app = Flask(__name__)
api = Api(app)

from positions import Positions

pos = Positions()


class APIServer(Resource):
    def get(self, target):
        if hasattr(pos, target):
            return getattr(pos, target)
        else:
            return ""

    def put(self, target):
        return ""


api.add_resource(APIServer, '/api/<string:target>')

if __name__ == '__main__':
    app.run(debug=True)
    # app.run()
