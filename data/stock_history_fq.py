#coding=utf-8
import urllib, urllib2, sys
import ssl
import json
import MySQLdb as mdb
import stock_sql
import datetime
import config


markets = ['sh','sz']
host = 'http://img1.money.126.net'
path = '/data/hs/klinederc/day/times'
method = 'GET'
bodys = {}


def processHistoryData():
	for market in markets:
		code_list = getCodeList(market)

		

		for code in code_list:
			conn = mdb.connect(host=config.mysql_ip, port=config.mysql_port,user=config.mysql_user,passwd=config.mysql_pass,db=config.mysql_db,charset='utf8')
			cursor = conn.cursor()

			content = None
			if market == 'sh':
				content = requestHistoryData('0'+code)
			else:
				content = requestHistoryData('1'+code)

			if content == None:
				continue
			json_content = json.loads(content)

			closes = json_content['closes']
			times = json_content['times']

			for i in range(0,len(times),1):
				close = closes[i]
				time = times[i]

				c = datetime.datetime.strptime(time,'%Y%m%d');
				date = c.strftime('%Y-%m-%d');

				saveToDB(code,date,close,cursor)

			conn.commit()
			cursor.close()
			conn.close()



def requestHistoryData(code):
	try:
		url = host + path + '/' + code + '.json'
		request = urllib2.Request(url)
		ctx = ssl.create_default_context()
		ctx.check_hostname = False
		ctx.verify_mode = ssl.CERT_NONE
		response = urllib2.urlopen(request, context=ctx)
		content = response.read()
		return content
	except:
		return None

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

def saveToDB(code,date,fq_close_price,cursor):
	print('update code = ' + code + ',date = ' + date + ',fq_close_price = '+bytes(fq_close_price))
	cursor.execute(''.join(['UPDATE stock_history ',
							'SET stock_history.fq_close_price = %s ',
							'WHERE ',
								'stock_history.`code` = %s AND stock_history.date = %s ']),[fq_close_price,code,date])

if __name__ == '__main__':
	processHistoryData()
	#getStockList('sh')
