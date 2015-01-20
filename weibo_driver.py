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

def get_data(client):
	raw_data = client.statuses.public_timeline.get(count=10)
	statuses = raw_data['statuses']

	text = [i.get('text', '') for i in statuses]
	text_str = '#:-:#'.join(text)
	text_str += '\n'
	return text_str			

def send_data(conn, client):
	# data = get_data(client)
	data = 'hello, I am litaotao'
	conn.sendall(data.encode('utf-8'))
	print 'IN THREAD: send to {}, data length: {}'.format(str(conn), str(len(data)))
	conn.close()


