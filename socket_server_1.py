# -*- coding: utf-8 -*-

from weibo_driver import *

def socket_server(HOST, PORT):
	client = get_local_weibo_client() or get_weibo_client()

	# s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)  
	s = socket.socket()    
	s.bind((HOST, PORT))
	s.listen(10)
	
	while  True:
		print 'wait for connection ...'
		print '-----------------------'
		conn, addr = s.accept()
		print 'connect with {} : {}'.format(addr[0], str(addr[1]))
		thread.start_new_thread(send_data, (conn, client))		
	s.shutdown()


if __name__ == '__main__':
	HOST, PORT = '', 9999
	socket_server(HOST, PORT)
