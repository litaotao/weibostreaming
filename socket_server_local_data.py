# -*- coding: utf-8 -*-

from weibo_driver import *
from pymongo import MongoClient


MongoHost = 'localhost'
MongoPort = 27017


def socket_server(HOST, PORT):
	client = MongoClient(MongoHost, MongoPort)

	s = socket.socket()    
	s.bind((HOST, PORT))
	s.listen(10)
	
	conn_number = 1
	while  True:
		print 'wait for connection ...'
		print '-----------------------'
		conn, addr = s.accept()
		print 'connect with {} : {}'.format(addr[0], str(addr[1]))
		thread.start_new_thread(send_data, (conn, client, conn_number, 3))	
		conn_number += 1	
	s.shutdown()


if __name__ == '__main__':
	HOST, PORT = '', 9999
	socket_server(HOST, PORT)
