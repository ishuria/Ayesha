#coding=utf-8
import sys
import json
import MySQLdb as mdb
import stock_sql


#数据库配置
mysql_ip = '106.15.72.40'
mysql_port = 3306
mysql_user = 'ayesha'
mysql_pass = 'Ayesha_topaz77'
mysql_db = 'ayesha'


#content = '';
#with open('result.txt', 'r') as f:
#	content = f.read()
#	json_content = json.loads(content)
#	print(json_content['showapi_res_body']['allPages'])



def saveToDB(stock_json):
	conn = mdb.connect(host=mysql_ip, port=mysql_port,user=mysql_user,passwd=mysql_pass,db=mysql_db,charset='utf8')
	cursor = conn.cursor()
	stockType = stock_json['stockType']
	market = stock_json['market']
	name = stock_json['name']
	state = stock_json['state']
	currcapital = stock_json['currcapital']
	profit_four = stock_json['profit_four']
	code = stock_json['code']
	totalcapital = stock_json['totalcapital']
	mgjzc = stock_json['mgjzc']
	pinyin = stock_json['pinyin']
	listing_date = stock_json['listing_date']
	ct = stock_json['ct']

	count = cursor.execute(stock_sql.stock_count_sql , [code])
	#如果有记录，更新
	if count == 1:
		cursor.execute(stock_sql.stock_update_sql,[stockType,market,name,state,currcapital,profit_four,totalcapital,mgjzc,pinyin,listing_date,ct,code])
	#否则新增数据
	else:
		cursor.execute(stock_sql.stock_insert_sql,[stockType,market,name,state,currcapital,profit_four,code,totalcapital,mgjzc,pinyin,listing_date,ct])
	conn.commit()
	cursor.close()
	conn.close()



if __name__ == '__main__':
	saveToDB(json.loads('{"stockType":"A","market":"sh","name":"阳煤化工","state":"1","currcapital":"175639.0906","profit_four":"-8.9886","code":"600691","totalcapital":"175678.6906","mgjzc":"2.115349","pinyin":"ymhg","listing_date":"1993-11-19","ct":"2016-10-16 15:38:45.467"}'))
