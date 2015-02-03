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
	all_tokens = None
	if 'token.json' not in os.listdir('.'):
		print 'no token.json file'
		return None
	else:
		f = file('token.json', 'r')
		all_tokens = json.load(f)
		f.close()
	if not all_tokens:
		return None

	token = all_tokens.pop(0)
	APP_KEY = token['APP_KEY']
	APP_SECRET = token['APP_SECRET']
	CALLBACK_URL = token['CALLBACK_URL']
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
		self.next = 0

	def gen_all_client(self):
		ls = os.listdir('.')
		tokens = None
		if self.token_file not in ls:
			self.build_token()
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

	def build_token(self):
		all_tokens = []
		tmp = {}
		app_key = ['1029531902', '3966337806', '194387379', '1867239709',
					'1414255866', '2153060451']
		app_secret = ['424e3c69dc24234ce958a577fcaa0552', '2aa611573beebb85477d96661dcb7338',
					  '00d508e40faf7770d7733a62e0cc736f', '75bc38d733f1d244d212264c3afb62de',
					  'ca60eb889706e203040ce4c32d9f9763', '4f14597150e881f6d6fece5761b56f09']
		callback_url = 'http://litaotao.github.io'

		for i in range(len(app_key)):
			A_K = app_key[i]
			A_S = app_secret[i]
			C_U = callback_url
			client = APIClient(A_K, A_S, C_U)
			print 'authorize_url: ', client.get_authorize_url()
			code = raw_input('code: ')
			r = client.request_access_token(code)
			access_token = r.access_token 	# 新浪返回的token，类似abc123xyz456
			expires_in = r.expires_in 		# token过期的UNIX时间：http://zh.wikipedia.org/wiki/UNIX%E6%97%B6%E9%97%B4
			tmp['APP_KEY'] = A_K
			tmp['APP_SECRET'] = A_S
			tmp['CALLBACK_URL'] = C_U
			tmp['token'] = access_token
			tmp['expires'] = expires_in
			all_tokens.append(tmp)
			tmp = {}
		f = file(self.token_file, 'w')
		json.dump(all_tokens, f)
		f.close()

	def get_client(self):
		if self.next == len(self.pool):
			self.next = 0
		return self.pool[self.next]
