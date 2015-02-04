# -*- coding: utf-8 -*-

import os
import sys


MONGOEXPORT = """d:/mongodb-2.4.10/bin/mongoexport.exe -h {}:{} -d {} -c {} -f {} """
PARAMETERS = """ -q "{"index": {"$lte": {}, "$gt": {}}}" -o {}"""

#-h localhost:27017  -d sinaweibo -c history -f index,msg -q "{"index": {"$lte": 10, "$gt": 5}}"  -o ../sina_history.dat


def export(command, start, end, dst):
	command = command + PARAMETERS.format(start, end, dst)
	os.system(command)
	return None

def build_command(host, port, db, collection, field):
	command = MONGOEXPORT.format(host, port, db, collection, field)
	return command

def main():
	host = 'localhost'
	port = 27017
	db, collection, field, start, end, step = sys.argv[1:]
	dst = '{}-{}'.format(db, collection) + '-{:0>4d}.dat'
	command = build_command(host, port, db, collection, field)
	start = int(start)
	end = int(end)
	step = int(step)
	count = 1

	while start + step < end:
		tmp_dst = dst.format(count)
		export(command, start, start+step, dst)
		start += step
		count += 1

	print 'Export done ...'


if __name__ == '__main__':
	import pdb; pdb.set_trace()
	main()


