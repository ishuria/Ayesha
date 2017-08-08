#coding=utf-8
import urllib, urllib2, sys
import ssl
import json
import MySQLdb as mdb
import stock_sql

#常量
#'sh','sz',
markets = ['hk']
host = 'https://ali-stock.showapi.com'
path = '/stocklist'
method = 'GET'
appcode = 'f86b2760312b41a0b9ef963ceca71b0b'
bodys = {}

#数据库配置
mysql_ip = '106.15.72.40'
mysql_port = 3306
mysql_user = 'ayesha'
mysql_pass = 'Ayesha_topaz77'
mysql_db = 'ayesha'

def processStockData():
	for market in markets:
		curr_page = 1
		total_pages = 99
		while curr_page < total_pages:
			print('curr_page = '+bytes(curr_page)+', market = '+market)
			content = requestContent(market,curr_page)
			#将返回的字符串转换为json对象
			json_content = json.loads(content)
			#提取全部页数
			total_pages = int(json_content['showapi_res_body']['allPages'])
			contentlist = json_content['showapi_res_body']['contentlist']
			processContentList(contentlist)
			#如果当前请求的页数没有达到全部页数，则当前页+1
			if(curr_page < total_pages):
				curr_page = curr_page + 1

#查询market,page条件下的股票产品
def requestContent(market,page):
	url = host + path + '?' + 'market=' + market + '&' + 'page='+bytes(page)
	request = urllib2.Request(url)
	request.add_header('Authorization', 'APPCODE ' + appcode)
	ctx = ssl.create_default_context()
	ctx.check_hostname = False
	ctx.verify_mode = ssl.CERT_NONE
	response = urllib2.urlopen(request, context=ctx)
	content = response.read()
	return content

def processContentList(content_list_json):
	for content in content_list_json:
		saveToDB(content)


def saveToDB(stock_json):
	conn = mdb.connect(host=mysql_ip, port=mysql_port,user=mysql_user,passwd=mysql_pass,db=mysql_db,charset='utf8')
	cursor = conn.cursor()
	stockType = ''
	if stock_json.has_key('stockType'):
		stockType = stock_json['stockType']

	market = ''
	if stock_json.has_key('market'):
		market = stock_json['market']

	name = ''
	if stock_json.has_key('name'):
		name = stock_json['name']

	state = ''
	if stock_json.has_key('state'):
		state = stock_json['state']

	currcapital = ''
	if stock_json.has_key('currcapital'):
		currcapital = stock_json['currcapital']

	profit_four = ''
	if stock_json.has_key('profit_four'):
		profit_four = stock_json['profit_four']

	code = ''
	if stock_json.has_key('code'):
		code = stock_json['code']

	totalcapital = ''
	if stock_json.has_key('totalcapital'):
		totalcapital = stock_json['totalcapital']

	mgjzc = ''
	if stock_json.has_key('mgjzc'):
		mgjzc = stock_json['mgjzc']

	pinyin = ''
	if stock_json.has_key('pinyin'):
		pinyin = stock_json['pinyin']

	listing_date = ''
	if stock_json.has_key('listing_date'):
		listing_date = stock_json['listing_date']

	ct = ''
	if stock_json.has_key('ct'):
		ct = stock_json['ct']

	cursor.execute(stock_sql.stock_count_sql , [code])
	result = cursor.fetchone()
	count = result[0]
	#如果有记录，更新
	if count == 1:
		print('update code = ' + code)
		cursor.execute(stock_sql.stock_update_sql,[stockType,market,name,state,currcapital,profit_four,totalcapital,mgjzc,pinyin,listing_date,ct,code])
	#否则新增数据
	else:
		print('insert code = ' + code)
		cursor.execute(stock_sql.stock_insert_sql,[stockType,market,name,state,currcapital,profit_four,code,totalcapital,mgjzc,pinyin,listing_date,ct])
	conn.commit()
	cursor.close()
	conn.close()


if __name__ == '__main__':
	processStockData()

