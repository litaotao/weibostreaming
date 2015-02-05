# -*- coding: utf-8 -*-

from weibo_driver import *


def socket_server(HOST, PORT):
	client = None
	s = socket.socket()    
	s.bind((HOST, PORT))
	s.listen(10)
	
	conn_number = 1
	while  True:
		print 'Wait for connection ...'
		conn, addr = s.accept()
		print 'Connection No.{},  with {} : {}'.format(conn_number, addr[0], str(addr[1]))
		print '-----------------------\n'
		thread.start_new_thread(send_data, (conn, client, 3, conn_number))	
		conn_number += 1
	
	s.close()
	s.shutdown()


if __name__ == '__main__':
	HOST, PORT = '', 9999
	socket_server(HOST, PORT)
