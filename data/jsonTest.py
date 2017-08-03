#coding=utf-8
import sys
import json
import MySQLdb as mdb


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
	code = stock_json['code']
	count = cursor.execute('select * from stock where code = %s' , [code])
	if count == 1:
		cursor.execute('update stock set stockType = %s where code = %s',['A',code])
	record = cursor.fetchone()
	print(record)
	conn.commit()
	cursor.close()
	conn.close()

	#如果已经有记录，



if __name__ == '__main__':
	saveToDB(json.loads('{"stockType":"A","market":"sh","name":"阳煤化工","state":"1","currcapital":"175639.0906","profit_four":"-8.9886","code":"600691","totalcapital":"175678.6906","mgjzc":"2.115349","pinyin":"ymhg","listing_date":"1993-11-19","ct":"2016-10-16 15:38:45.467"}'))
