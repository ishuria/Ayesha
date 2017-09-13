# -*- coding: UTF-8 -*-  
import subprocess
import config
import MySQLdb as mdb
import stock_sql
import datetime
import os
import sys
import time

conn = None
cursor = None

def start_learn(code,batch_size,time_step,term,begin,end):
	enddate = datetime.datetime(int(end[0:4]),int(end[5:7]),int(end[8:10]))
	begindate = datetime.datetime(int(begin[0:4]),int(begin[5:7]),int(begin[8:10]))
	while begindate <= enddate:
		train_date = begindate.strftime('%Y-%m-%d')
		command = 'python stock_learn_3.py' + ' ' + code + ' ' + str(batch_size) + ' ' + str(time_step) + ' ' + term + ' ' + train_date
		p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		for line in p.stdout.readlines():
			print line,
		retval = p.wait()
		begindate = begindate + datetime.timedelta(days=1)

if __name__ == '__main__':
	start_learn('600000',30,30,'30','2005-01-01','2012-12-31')