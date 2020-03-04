import os
import sys
import uuid
import json
import zipfile
from flask import Flask, request, abort, jsonify, send_from_directory, render_template
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import datetime
app = Flask(__name__)
import models, resources
from concurrent.futures import ThreadPoolExecutor
from time import sleep

FULL_DATABASE = 'sqlite:///D:\\rohan\\Documents\\CS261 Coursework\\database_cs261_full.db'
PARTIAL_DATABASE = 'sqlite:///database_cs261_2.0/db'

api = Api(app)
CORS(app)

api.add_resource(resources.Currencies, '/api/currencies')
api.add_resource(resources.Companies, '/api/companies')
api.add_resource(resources.Products, '/api/products')
api.add_resource(resources.Trades, '/api/trades')
api.add_resource(resources.CheckTrade, '/api/check_trade')
api.add_resource(resources.Reports, '/api/reports')
api.add_resource(resources.Rules, '/api/rules')
api.add_resource(resources.Users, '/api/users')
app.config['SQLALCHEMY_DATABASE_URI'] = PARTIAL_DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

#executor = ThreadPoolExecutor(1)
#executor.submit(resources.run_cron_job)

@app.route('/')
def index():
    return jsonify({'message':'Welcome to Deustche Bank'})

if __name__=="__main__":
    app.run(debug=True,port=8002,host = '0.0.0.0')
