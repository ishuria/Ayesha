#coding=utf-8
import urllib, urllib2, sys
import ssl
import json
import MySQLdb as mdb
import stock_sql
import datetime
import config


markets = ['sh']
host = 'https://ali-stock.showapi.com'
path = '/sz-sh-stock-history'
method = 'GET'
bodys = {}


def processHistoryData(begin,end):
	for market in markets:
		code_list = getCodeList(market)
		for code in code_list:
			enddate = datetime.datetime(int(end[0:4]),int(end[5:7]),int(end[8:10]))
			begindate = datetime.datetime(int(begin[0:4]),int(begin[5:7]),int(begin[8:10]))
			
			sub_begindate = ''
			sub_enddate = ''
			while enddate >= begindate:
				if enddate + datetime.timedelta(days=-31) < begindate:
					sub_begindate = begindate.strftime('%Y-%m-%d')
					sub_enddate = (enddate).strftime('%Y-%m-%d')
				else:
					sub_begindate = (enddate + datetime.timedelta(days=-31)).strftime('%Y-%m-%d')
					sub_enddate = (enddate).strftime('%Y-%m-%d')

				print('begin = '+sub_begindate)
				print('end = '+sub_enddate)
				content = requestHistoryData(sub_begindate,sub_enddate,code)
				json_content = json.loads(content)

				price_list = json_content['showapi_res_body']['list']
				processPriceList(price_list)
				enddate = enddate + datetime.timedelta(days=-32)




def requestHistoryData(begin,end,code):
	url = host + path + '?' + 'begin=' + begin + '&code=' + code + '&end=' + end
	request = urllib2.Request(url)
	request.add_header('Authorization', 'APPCODE ' + config.appcode)
	ctx = ssl.create_default_context()
	ctx.check_hostname = False
	ctx.verify_mode = ssl.CERT_NONE
	response = urllib2.urlopen(request, context=ctx)
	content = response.read()
	return content


def getJsonValue(jsonObject,key):
	value = ''
	if jsonObject.has_key(key):
		value = jsonObject[key]
	return value


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

'''
{
	"min_price": "11.920",//最低价
	"market": "sh",//市场，例如sh
	"trade_num": "8111935",//交易手数
	"trade_money": "99310240",//交易金额元
	"close_price": "12.110",//收盘价
	"open_price": "12.680",//开盘价
	"code": "600004",//股票代码
	"max_price": "12.680",//最高价
	"date": "2015-09-01"//日期，例如2015-09-02
}
'''

def processPriceList(price_list):
	for price in price_list:
		saveToDB(price)


def saveToDB(stock_json):
	conn = mdb.connect(host=config.mysql_ip, port=config.mysql_port,user=config.mysql_user,passwd=config.mysql_pass,db=config.mysql_db,charset='utf8')
	cursor = conn.cursor()
	min_price = getJsonValue(stock_json,'min_price')
	market = getJsonValue(stock_json,'market')
	trade_num = getJsonValue(stock_json,'trade_num')
	trade_money = getJsonValue(stock_json,'trade_money')
	close_price = getJsonValue(stock_json,'close_price')
	open_price = getJsonValue(stock_json,'open_price')
	code = getJsonValue(stock_json,'code')
	max_price = getJsonValue(stock_json,'max_price')
	date = getJsonValue(stock_json,'date')

	cursor.execute(stock_sql.stock_history_count_sql , [code, date])
	result = cursor.fetchone()
	count = result[0]
	#如果有记录，更新
	if count == 1:
		print('update code = ' + code + ',date = ' + date)
		cursor.execute(stock_sql.stock_history_update_sql,[min_price,market,trade_num,trade_money,close_price,open_price,max_price,code,date])
	#否则新增数据
	else:
		print('insert code = ' + code + ',date = ' + date)
		cursor.execute(stock_sql.stock_history_insert_sql,[min_price,market,trade_num,trade_money,close_price,open_price,code,max_price,date])
	conn.commit()
	cursor.close()
	conn.close()


if __name__ == '__main__':
	processHistoryData('2017-07-01','2017-07-31')
	#getStockList('sh')
