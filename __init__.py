# -*- coding: utf-8 -*-

import ConfigParser
from pymongo import MongoClient


# read community configurations
cf = ConfigParser.ConfigParser()
cf.read('app.cfg')


# SINA_APP_CONFIG
APP_KEY = cf.get('SINA_APP_CONFIG', 'APP_KEY')
APP_SECRET = cf.get('SINA_APP_CONFIG', 'APP_SECRET')
CALLBACK_URL = cf.get('SINA_APP_CONFIG', 'CALLBACK_URL')

APP_KEY = eval(APP_KEY)
APP_SECRET = eval(APP_SECRET)

# MongoDB client
MongoHost = cf.get('MongoDB', 'host')
MongoPort = cf.get('MongoDB', 'port')
mongo_client = MongoClient(MongoHost, int(MongoPort))

