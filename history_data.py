# -*- coding: utf-8 -*-


import weibo_driver as wd 
from pymongo import MongoClient
import time


def init_all_client():
	pass

def get_client():
	pass

def get_history_data():
	"""
	get the history public weibo message every 5 seconds.
	"""
	mongo_client = MongoClient('localhost', 27017)
	weibo_client = wd.get_client() 
	while True:
		try:
			data = wd.get_data(weibo_client, data_type=3, count=200)
		except:
			print 'Oops, this client is out of request limit, user another one'
			weibo_client = get_client(weibo_client)

		wd.sendto_mongo(mongo_client, data)
		print 'get {} piece of data'.format(len(data))
		time.sleep(5)


if __name__ == '__main__':
	get_history_data()

