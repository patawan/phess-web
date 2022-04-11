# -*- coding: utf-8 -*-
"""
Created on Mon Oct 14 20:46:43 2019

@author: phess
"""


# respective model URLs are as follows:
# http://0.0.0.0:5000/michael_model
# http://0.0.0.0:5000/jim_model
# http://0.0.0.0:5000/pam_model
# http://0.0.0.0:5000/dwight_model

import os
import json
from flask import Flask
from flask import render_template, make_response
from flask_restful import reqparse, abort, Api, Resource, request
import markovify as mk


port = int(os.getenv('PORT', '5000'))

app = Flask(__name__)
api = Api(app)
cwd = os.getcwd()


michael_path = cwd + "/michael_model_json.txt"
dwight_path = cwd + "/dwight_model_json.txt"
jim_path = cwd + "/jim_model_json.txt"
pam_path = cwd + "/pam_model_json.txt"

with open(michael_path, "r") as fr:
    michael_model_json = json.load(fr)

with open(dwight_path, "r") as fr:
    dwight_model_json = json.load(fr)

with open(jim_path, "r") as fr:
    jim_model_json = json.load(fr)

with open(pam_path, "r") as fr:
    pam_model_json = json.load(fr)

reconstituted_model_michael = mk.Text.from_json(michael_model_json)
reconstituted_model_dwight = mk.Text.from_json(dwight_model_json)
reconstituted_model_jim = mk.Text.from_json(jim_model_json)
reconstituted_model_pam = mk.Text.from_json(pam_model_json)


class landing(Resource):
    def get(self):
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template('index.html'),200,headers)


class MichaelModel(Resource):
    def get(self):
        # make a line
        michael_line = reconstituted_model_michael.make_sentence(tries=100)
        m = {"Michael Line": michael_line}
        # create JSON object
        output = json.dumps(m)
        output=json.loads(output)

        return output


class JimModel(Resource):
    def get(self):
        # make a line
        jim_line = reconstituted_model_jim.make_sentence(tries=100)
        j = {"Jim Line": jim_line}
        # create JSON object
        output = json.dumps(j)
        output=json.loads(output)

        return output


class PamModel(Resource):
    def get(self):
        # make a line
        pam_line = reconstituted_model_pam.make_sentence(tries=100)
        p = {"Pam Line": pam_line}
        # create JSON object
        output = json.dumps(p)
        output=json.loads(output)

        return output


class DwightModel(Resource):
    def get(self):
        # make a line
        dwight_line = reconstituted_model_dwight.make_sentence(tries=100)
        d = {"Dwight Line": dwight_line}
        # create JSON object
        output = json.dumps(d)
        output=json.loads(output)

        return output

class HelloTori(Resource):
    def get(self):
        return {'Hello': 'I love you! <3'}


api.add_resource(landing, "/")
api.add_resource(MichaelModel, '/michael_model')
api.add_resource(JimModel, '/jim_model')
api.add_resource(PamModel, '/pam_model')
api.add_resource(DwightModel, '/dwight_model')
api.add_resource(HelloTori, "/luvu")

if __name__ == '__main__':
    #app.run(debug=True)
    app.run(host='0.0.0.0', port=port)