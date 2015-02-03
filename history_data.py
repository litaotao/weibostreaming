# -*- coding: utf-8 -*-


import weibo_driver as wd 
from pymongo import MongoClient
import time
import datetime


def get_history_data():
	"""
	get the history public weibo message every 5 seconds.
	"""
	SinaWeiboClient = wd.SinaWeiboClient('token.json')
	SinaWeiboClient.gen_all_client()
	mongo_client = MongoClient('localhost', 27017)
	weibo_client = SinaWeiboClient.get_client() 
	count = 0

	while True:
	# import pdb; pdb.set_trace()
	# for i in range(10):
		try:
			data = wd.get_data(weibo_client, data_type=3, count=200)
		except:
			print 'Oops, this client is out of request limit, user another one'
			weibo_client = SinaWeiboClient.get_client()
			data = wd.get_data(weibo_client, data_type=3, count=200)
			continue

		wd.sendto_mongo(mongo_client, data)
		print 'No.{}, time: {}, weibo number: {}'.format(count,
				datetime.datetime.now().isoformat(), len(data))

		count += 1
		time.sleep(5)


if __name__ == '__main__':
	get_history_data()

