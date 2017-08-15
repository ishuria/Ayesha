#coding=utf-8
import os
import urllib2
import stock_sql
import config
import MySQLdb as mdb
from itertools import islice  
import datetime

host = 'http://quotes.money.163.com/service/chddata.html'
markets = ['sh','sz']

def processCSV(file_name,market):
	conn = mdb.connect(host=config.mysql_ip, port=config.mysql_port,user=config.mysql_user,passwd=config.mysql_pass,db=config.mysql_db,charset='utf8')
	cursor = conn.cursor()
	with open(file_name) as f:
		lines = f.readlines()
		for line in islice(lines, 1, None): 
			saveToDB(cursor,line,market)
	conn.commit()
	cursor.close()
	conn.close()

def processHistoryData(begin,end):
	enddate = datetime.datetime(int(end[0:4]),int(end[5:7]),int(end[8:10]))
	begindate = datetime.datetime(int(begin[0:4]),int(begin[5:7]),int(begin[8:10]))

	begin = begindate.strftime('%Y%m%d')
	end = enddate.strftime('%Y%m%d')
	for market in markets:
		code_list = getCodeList(market)
		line_num = 0
		for code in code_list:
			if market == 'sh':
				requestHistoryData(begin,end,code,0)
			else:
				requestHistoryData(begin,end,code,1)
			processCSV(code + '.csv',market)
			os.remove(code + '.csv')

def trimValue(value):
	value = value.replace('\'','')
	if value == 'None' or value == '':
		value = None
	return value

def saveToDB(cursor,stock_line,market):
	contents = stock_line.split(',')

	#日期0,股票代码1,名称2,收盘价3,最高价4,最低价5,开盘价6,前收盘7,涨跌额8,涨跌幅9,换手率10,成交量11,成交金额12,总市值13,流通市值14,成交笔数15

	#最低价5
	min_price = trimValue(contents[5])
	try:
		min_price = format(float(min_price),'0.2f')
	except:
		min_price = None
		
	#成交量11
	trade_num = trimValue(contents[11])
	try:
		trade_num = format(float(trade_num),'0.4f')
	except:
		trade_num = None

	#成交金额12
	trade_money = trimValue(contents[12])
	try:
		trade_money = format(float(trade_money),'0.4f')
	except:
		trade_money = None

	#收盘价3
	close_price = trimValue(contents[3])
	try:
		close_price = format(float(close_price),'0.2f')
	except:
		close_price = None

	#开盘价6
	open_price = trimValue(contents[6])
	try:
		open_price = format(float(open_price),'0.2f')
	except:
		open_price = None

	code = trimValue(contents[1])

	#最高价4
	max_price = trimValue(contents[4])
	try:
		max_price = format(float(max_price),'0.2f')
	except:
		max_price = None

	date = trimValue(contents[0])

	#前收盘7
	last_close_price = trimValue(contents[7])
	try:
		last_close_price = format(float(last_close_price),'0.2f')
	except:
		last_close_price = None

	#涨跌额8
	increase = trimValue(contents[8])
	try:
		increase = format(float(increase),'0.2f')
	except:
		increase = None

	#涨跌幅9
	increase_rate = trimValue(contents[9])
	try:
		increase_rate = format(float(increase_rate),'0.4f')
	except:
		increase_rate = None

	#换手率10
	turnover_rate = trimValue(contents[10])
	try:
		turnover_rate = format(float(turnover_rate),'0.4f')
	except:
		turnover_rate = None

	#总市值13
	total_value = trimValue(contents[13])
	try:
		total_value = format(float(total_value),'0.4f')
	except:
		total_value = None
	
	#流通市值14
	circulation_value = trimValue(contents[14])
	try:
		circulation_value = format(float(circulation_value),'0.4f')
	except:
		circulation_value = None


	cursor.execute(stock_sql.stock_history_count_sql_163 , [code, date])
	result = cursor.fetchone()
	count = result[0]
	#如果有记录，更新
	if count == 1:
		print('update code = ' + code + ',date = ' + date)
		cursor.execute(stock_sql.stock_history_update_sql_163,[min_price,market,trade_num,trade_money,close_price,open_price,max_price,last_close_price,increase,increase_rate,turnover_rate,total_value,circulation_value,code,date])
	#否则新增数据
	else:
		print('insert code = ' + code + ',date = ' + date)
		cursor.execute(stock_sql.stock_history_insert_sql_163,[min_price,market,trade_num,trade_money,close_price,open_price,code,max_price,date,last_close_price,increase,increase_rate,turnover_rate,total_value,circulation_value])
	

def getCodeList(market):
	conn = mdb.connect(host=config.mysql_ip, port=config.mysql_port,user=config.mysql_user,passwd=config.mysql_pass,db=config.mysql_db,charset='utf8')
	cursor = conn.cursor()

	stock_list = []
	cursor.execute(stock_sql.stock_market_select_sql , [market])
	results = cursor.fetchall()
	for result in results:
		stock_list.append(result[6])

	conn.commit()
	cursor.close()
	conn.close()
	return stock_list

def requestHistoryData(begin,end,code,market_code):
	url = host + '?code=' + bytes(market_code) + bytes(code) + '&start=' + begin + '&end=' + end 
	print(url)
	f = urllib2.urlopen(url) 
	data = f.read() 
	with open(code + '.csv', "w") as file:     
	    file.write(data)

if __name__ == '__main__':
	processHistoryData('2017-08-14','2017-08-14')
	#print '{:.4f}'.format(float('1.83549222401e+12'))
	#print(float(None))

	'''
	begin = '2017-01-01'
	end = '2017-07-31'

	enddate = datetime.datetime(int(end[0:4]),int(end[5:7]),int(end[8:10]))
	begindate = datetime.datetime(int(begin[0:4]),int(begin[5:7]),int(begin[8:10]))

	begin = begindate.strftime('%Y%m%d')
	end = enddate.strftime('%Y%m%d')

	print(begin)
	print(end)
	'''


