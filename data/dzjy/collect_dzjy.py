# -*- coding: UTF-8 -*-  
import config
import MySQLdb as mdb
import urllib, urllib2, sys
import ssl
import json

conn = None
cursor = None

def updateDZJY(page):
	content = getDZJYdata(page)
	json_content = json.loads(content)
	for i in range(len(json_content)):
		TDATE = json_content[i]["TDATE"]
		SECUCODE = json_content[i]["SECUCODE"]
		SNAME = json_content[i]["SNAME"]
		PRICE = json_content[i]["PRICE"]
		TVOL = json_content[i]["TVOL"]
		TVAL = json_content[i]["TVAL"]
		BUYERCODE = json_content[i]["BUYERCODE"]
		BUYERNAME = json_content[i]["BUYERNAME"]
		SALESCODE = json_content[i]["SALESCODE"]
		SALESNAME = json_content[i]["SALESNAME"]
		Stype = json_content[i]["Stype"]
		Unit = json_content[i]["Unit"]
		RCHANGE = None if json_content[i]["RCHANGE"]=='-' else json_content[i]["RCHANGE"]
		CPRICE = None if json_content[i]["CPRICE"]=='-' else json_content[i]["CPRICE"]
		YSSLTAG = None if json_content[i]["YSSLTAG"]=='-' else json_content[i]["YSSLTAG"]
		Zyl = None if json_content[i]["Zyl"]=='-' else json_content[i]["Zyl"]
		Cjeltszb = None if json_content[i]["Cjeltszb"]=='-' else json_content[i]["Cjeltszb"]
		RCHANGE1DC = None if json_content[i]["RCHANGE1DC"]=='-' else json_content[i]["RCHANGE1DC"]
		RCHANGE5DC = None if json_content[i]["RCHANGE5DC"]=='-' else json_content[i]["RCHANGE5DC"]
		RCHANGE10DC = None if json_content[i]["RCHANGE10DC"]=='-' else json_content[i]["RCHANGE10DC"]
		RCHANGE20DC = None if json_content[i]["RCHANGE20DC"]=='-' else json_content[i]["RCHANGE20DC"]
		TEXCH = json_content[i]["TEXCH"]

		cursor.execute(''.join(['insert into dzjy_history ( '
									'TDATE, ',
									'SECUCODE, ',
									'SNAME, ',
									'PRICE, ',
									'TVOL, ',
									'TVAL, ',
									'BUYERCODE, ',
									'BUYERNAME, ',
									'SALESCODE, ',
									'SALESNAME, ',
									'Stype, ',
									'Unit, ',
									'RCHANGE, ',
									'CPRICE, ',
									'YSSLTAG, ',
									'Zyl, ',
									'Cjeltszb, ',
									'RCHANGE1DC, ',
									'RCHANGE5DC, ',
									'RCHANGE10DC, ',
									'RCHANGE20DC, ',
									'TEXCH ) values ( ',
									'%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s )  ']),[
									TDATE,
									SECUCODE,
									SNAME,
									PRICE,
									TVOL,
									TVAL,
									BUYERCODE,
									BUYERNAME,
									SALESCODE,
									SALESNAME,
									Stype,
									Unit,
									RCHANGE,
									CPRICE,
									YSSLTAG,
									Zyl,
									Cjeltszb,
									RCHANGE1DC,
									RCHANGE5DC,
									RCHANGE10DC,
									RCHANGE20DC,
									TEXCH])


	conn.commit()






def getDZJYdata(page):
	url = 'http://dcfm.eastmoney.com/em_mutisvcexpandinterface/api/js/get?type=DZJYXQ&token=70f12f2f4f091e459a279469fe49eca5&cmd=&st={sortType}&sr={sortRule}&p='+str(page)+'&ps={pageSize}'
	request = urllib2.Request(url)
	ctx = ssl.create_default_context()
	ctx.check_hostname = False
	ctx.verify_mode = ssl.CERT_NONE
	response = urllib2.urlopen(request, context=ctx)
	content = response.read()
	return content

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
	for i in range(162):
		updateDZJY(i+1)
	db_close()