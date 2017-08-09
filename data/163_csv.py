#coding=utf-8
import os
import urllib2
import stock_sql
import config
import MySQLdb as mdb
from itertools import islice  


host = 'http://quotes.money.163.com/service/chddata.html'
markets = ['sh','sz']



def processCSV(file_name,market):
	conn = mdb.connect(host=config.mysql_ip, port=config.mysql_port,user=config.mysql_user,passwd=config.mysql_pass,db=config.mysql_db,charset='utf8')
	cursor = conn.cursor()
	with open(file_name) as f:
		lines = f.readlines()
		for line in islice(lines, 1, None):  
			#print line.split(',')
			saveToDB(cursor,line,market)
	conn.commit()
	cursor.close()
	conn.close()


def processHistoryData(begin,end):
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



def saveToDB(cursor,stock_line,market):
	

	contents = stock_line.split(',')
	#日期0,股票代码1,名称2,收盘价3,最高价4,最低价5,开盘价6,前收盘7,涨跌额8,涨跌幅9,换手率10,成交量11,成交金额12,总市值13,流通市值14,成交笔数15
	min_price = contents[5]
	trade_num = contents[11]
	trade_money = contents[12]
	close_price = contents[3]
	open_price = contents[6]
	code = contents[1].replace('\'','')
	max_price = contents[4]
	date = contents[0]
	last_close_price = contents[7]
	increase = contents[8]
	increase_rate = contents[9]
	turnover_rate = contents[10]

	total_value = ''
	try:
		total_value = '{:.4f}'.format(float(contents[13]))  
	except:
		total_value = ''
	
	circulation_value = ''
	try:
		circulation_value = '{:.4f}'.format(float(contents[14]))
	except:
		circulation_value = ''


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
	f = urllib2.urlopen(url) 
	data = f.read() 
	with open(code + '.csv', "w") as file:     
	    file.write(data)

if __name__ == '__main__':
	processHistoryData('20000101','20170809')
	#print '{:.4f}'.format(float('1.83549222401e+12'))
	


