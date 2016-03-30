# -*- coding: utf-8 -*-

"""
pmserver.py

porfolio monitor server

@author: yudi.wu
"""

from flask import Flask, request
from flask.ext.restful import Resource, Api

app = Flask(__name__)
api = Api(app)

from positions import Positions

pos = Positions()


class PMServer(Resource):
    def get(self, target):
        if hasattr(pos, target):
            return getattr(pos, target)
        else:
            return ""

    def put(self, target):
        return ""


api.add_resource(PMServer, '/api/<string:target>')

if __name__ == '__main__':
    app.run(debug=True)
    # app.run()
