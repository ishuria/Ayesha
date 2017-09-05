# -*- coding: UTF-8 -*-  
import subprocess
import config
import MySQLdb as mdb
import stock_sql
import datetime
import os
import sys
import time



#市场
markets = ['sh','sz']

conn = None
cursor = None

def start_learn(batch_size,time_step,term):
	for market in markets:
		code_list = getCodeList(market)
		for code in code_list:
			#获取这个代码的最新训练时间
			cursor.execute('select max(train_date) train_log from train_log t where t.`code` = %s',[code])
			result = cursor.fetchone()
			train_date = result[0]
			begindate = datetime.datetime(int(train_date[0:4]),int(train_date[5:7]),int(train_date[8:10]))
			curr_date = time.strftime('%Y-%m-%d')

			while train_date <= curr_date:

				

				code_path = '/home/ayesha/data/models/'+code
				model_path = code_path + '/' + term
				check_point_path = model_path + '/checkpoint'

				need_restore = False
				if os.path.isfile(check_point_path):
					need_restore = True

				command = 'python stock_learn_2.py' + ' ' + code + ' ' + str(batch_size) + ' ' + str(time_step) + ' ' + term + ' ' + train_date + ' ' + train_date + ' ' + str(need_restore)
				p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
				for line in p.stdout.readlines():
					print line,
				retval = p.wait()


				#记录下最新训练时间
				begindate += datetime.timedelta(days=1)
				train_date = begindate.strftime('%Y-%m-%d')
				cursor.execute('insert into train_log (`code`,train_date) values( %s,%s )',[code,train_date])
				conn.commit()








def getCodeList(market):
	stock_list = []
	cursor.execute(stock_sql.stock_market_select_sql , [market])
	results = cursor.fetchall()
	for result in results:
		stock_list.append(result[6])
	return stock_list


def db_connect():
	global conn
	global cursor
	conn = mdb.connect(host=config.mysql_ip, port=config.mysql_port,user=config.mysql_user,passwd=config.mysql_pass,db=config.mysql_db,charset='utf8')
	cursor = conn.cursor()

def db_close():
	#关闭数据库连接
	cursor.close()
	conn.close()


if __name__ == '__main__':
	db_connect()
	start_learn(30,30,'30')
	db_close()