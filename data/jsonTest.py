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

def processContentList(content_list_json):
	for content in content_list_json:
		saveToDB(content)


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

	cursor.execute(stock_sql.stock_count_sql , [code])
	result = cursor.fetchone()
	count = result[0]
	#如果有记录，更新
	if count == 1:
		print('update')
		cursor.execute(stock_sql.stock_update_sql,[stockType,market,name,state,currcapital,profit_four,totalcapital,mgjzc,pinyin,listing_date,ct,code])
	#否则新增数据
	else:
		print('insert')
		cursor.execute(stock_sql.stock_insert_sql,[stockType,market,name,state,currcapital,profit_four,code,totalcapital,mgjzc,pinyin,listing_date,ct])
	conn.commit()
	cursor.close()
	conn.close()

if __name__ == '__main__':
	#saveToDB(json.loads('{"stockType":"A","market":"sh","name":"阳煤化工","state":"1","currcapital":"175639.0906","profit_four":"-8.9886","code":"600691","totalcapital":"175678.6906","mgjzc":"2.115349","pinyin":"ymhg","listing_date":"1993-11-19","ct":"2016-10-16 15:38:45.467"}'))
	processContentList(json.loads('[{"stockType":"A","market":"sh","name":"阳煤化工","state":"1","currcapital":"175639.0906","profit_four":"-8.9886","code":"600691","totalcapital":"175678.6906","mgjzc":"2.115349","pinyin":"ymhg","listing_date":"1993-11-19","ct":"2016-10-16 15:38:45.467"},{"stockType":"B","market":"sh","name":"神奇B股","state":"1","currcapital":"5475.165","profit_four":"1.6572","code":"900904","totalcapital":"53407.1628","mgjzc":"4.436298","pinyin":"sqg","listing_date":"1992-07-22","ct":"2016-10-16 15:40:05.647"},{"stockType":"A","market":"sh","name":"保千里","state":-1,"currcapital":"102605.3132","profit_four":"8.3211","code":"600074","totalcapital":"243788.6049","mgjzc":"1.867589","pinyin":"bql","listing_date":"1997-06-23","ct":"2016-10-16 15:37:26.875"},{"stockType":"A","market":"sh","name":"浙大网新","state":"1","currcapital":"83074.7042","profit_four":"2.6886","code":"600797","totalcapital":"91404.3256","mgjzc":"2.488946","pinyin":"zdwx","listing_date":"1997-04-18","ct":"2016-10-16 15:38:58.875"},{"stockType":"A","market":"sh","name":"中国巨石","state":"1","currcapital":"291858.9041","profit_four":"16.3169","code":"600176","totalcapital":"291858.9041","mgjzc":"4.702533","pinyin":"zgjs","listing_date":"1999-04-22","ct":"2016-10-16 15:37:40.314"}]'))
