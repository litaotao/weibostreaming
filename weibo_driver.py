# -*- coding: utf-8 -*-

import socket
from weibo import APIClient
from time import sleep
import sys
import json
import os
import thread


def get_weibo_client():
	APP_KEY='1029531902'
	APP_SECRET='424e3c69dc24234ce958a577fcaa0552'
	CALLBACK_URL='http://litaotao.github.io'
	client = APIClient(app_key=APP_KEY, app_secret=APP_SECRET,
					   redirect_uri=CALLBACK_URL)

	print 'authorize_url: ', client.get_authorize_url()
	code = raw_input('code: ')

	client = APIClient(app_key=APP_KEY, app_secret=APP_SECRET, redirect_uri=CALLBACK_URL)
	r = client.request_access_token(code)
	access_token = r.access_token 	# 新浪返回的token，类似abc123xyz456
	expires_in = r.expires_in 		# token过期的UNIX时间：http://zh.wikipedia.org/wiki/UNIX%E6%97%B6%E9%97%B4
	print 'access_token: ', access_token
	print 'expires_in: ', expires_in
	# store in local
	f = file('token.json', 'w')
	token = dict(token=access_token, expires=expires_in)
	json.dump(token, f)
	f.close()
	client.set_access_token(access_token, expires_in)

	return client

def get_local_weibo_client():
	token = None
	if 'token.json' not in os.listdir('.'):
		print 'no token.json file'
		return None
	else:
		f = file('token.json', 'r')
		token = json.load(f)
		f.close()

	APP_KEY='1029531902'
	APP_SECRET='424e3c69dc24234ce958a577fcaa0552'
	CALLBACK_URL='http://litaotao.github.io'
	client = APIClient(app_key=APP_KEY, app_secret=APP_SECRET,
					   redirect_uri=CALLBACK_URL)
	access_token = token['token']
	expires_in = token['expires']

	client.set_access_token(access_token, expires_in)

	return client

def get_data(client, data_type=1, count=200):
	raw_data = client.statuses.public_timeline.get(count=count)
	statuses = raw_data['statuses']

	# import pdb; pdb.set_trace()
	if data_type == 1:
		return raw_data
	elif data_type == 2:
		text = [i.get('text', '') for i in statuses]
		text_str = '#:-:#'.join(text)
		text_str += '\n'
		return text_str			
	else:
		res = []
		tmp = {}
		for i in statuses:
			tmp['created_at'] = i['created_at']
			tmp['text'] = i['text']
			tmp['name'] = i['user']['name']
			tmp['location'] = i['user']['location']
			res.append(tmp)
			tmp = {}
		return res

def send_data(conn, client):
	# data = get_data(client)
	data = 'hello, I am litaotao'
	conn.sendall(data.encode('utf-8'))
	print '\nIN THREAD: send to {}, data length: {}'.format(str(conn), str(len(data)))
	conn.close()

def sendto_redis(r, name, data):
	"""
	store weibo message in redis server, and spark workers can connect
	to this redis server to fetch data.
	data is list of dict, each string is a utf-8 weibo message.
	"""
	for i in data:
		r.lpush(name, i)

def sendto_mongo(client, data):
	"""
	store history data in mongo.
	"""
	db = client.sinaweibo.history
	count = db.count()
	db.insert(dict(index=count+1, msg=data))


class SinaWeiboClient(object):
	"""docstring for SinaWeiboClient"""
	def __init__(self, token_file):
		self.token_file = token_file
		self.pool = []

	def __gen_all_client():
		ls = os.listdir()
		tokens = None
		if self.token_file not in ls:
			print 'current directory does not contain token file {}'.format(self.token_file)
			tokens = []
		else:
			f = file(self.token_file, 'r')
			tokens = json.load(f)
			f.close()
		for i in tokens:
			APP_KEY = i['APP_KEY']
			APP_SECRET = i['APP_SECRET']
			CALLBACK_URL = i['CALLBACK_URL']
			client = APIClient(APP_KEY, APP_SECRET, CALLBACK_URL)
			access_token = i['token']
			expires_in = i['expires']
			client.set_access_token(access_token, expires_in)

			self.pool.append(client)

	def get_client():
		if self.pool:
			return self.pool.pop(0)
		else:
			return None
