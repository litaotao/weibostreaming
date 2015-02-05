# -*- coding: utf-8 -*-

import socket
from weibo import APIClient
from time import sleep
import sys
import json
import os
import thread
from __init__ import APP_KEY, APP_SECRET, CALLBACK_URL, mongo_client



def get_weibo_client():
	APP_KEY = APP_KEY[0]
	APP_SECRET = APP_SECRET[0]
	CALLBACK_URL = CALLBACK_URL
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
			tmp['province'] = i['user']['province']
			tmp['city'] = i['user']['city']
			tmp['gender'] = i['user']['gender']
			tmp['idstr'] = i['user']['idstr']
			res.append(tmp)
			tmp = {}
		return res

def get_data_from_history(client, number):
	"""从本地mongo数据库中获取已存储的历史微博数据。
	一次返回1条数据咯~
	conn: 连接SS的worker
	client: MongoDB client
	number: 表示获取第几片(20条为一片)数据
	"""
	index = number * 1 / 201 + 1
	data = client.sinaweibo.history.find({'index': index}, {'_id': 0, 'msg': 1})
	data = data[0]
	msg = data['msg']
	res = msg[(number%200 - 1)  : number%200 ]

	return  'Recv No.{} '.format(number) + str(res) 

def send_data(conn, client, data_type, number=0):
	data = None
	if data_type == 1:
		data = 'hello, boys and sweet girls, I am litaotao . . .'
	elif data_type == 2:
		data = get_data(client)
	else:
		client = mongo_client
		data = get_data_from_history(client, number)

	conn.sendall(data.encode('utf-8'))
	print 'IN THREAD: send to {}, data length: {}'.format(str(conn), str(len(data)))
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
		app_key = APP_KEY
		app_secret = APP_SECRET
		callback_url = CALLBACK_URL

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
		client = self.pool[self.next]
		print '-----------------------------------'
		print 'Use client No.{}'.format(self.next)
		print '-----------------------------------\n\n'
		self.next += 1

		return client 
