# -*- coding: utf-8 -*-


import SocketServer as ss
from threading import Thread


class MessageSender(ss.BaseRequestHandler):
	"""docstring for ClassName"""
	def handle(self):
		print '--------------------------------------------'
		print 'New connection from : ', self.client_address
		data = 'hello, I am litaotao'
		self.request.send(data)		
		print 'Send to {}, data length: {}'.format(str(self.client_address), str(len(data)))
		print ''

def start_server(HOST, PORT):
	WORKERS = 20
	serv = ss.TCPServer((HOST, PORT), MessageSender)
	print 'Initialize thread pool ...'
	for n in range(WORKERS):
		t = Thread(target=serv.serve_forever)
		t.daemon = True
		t.start()
	print 'Start server ...\n'
	serv.serve_forever()
	serv.shutdown()

