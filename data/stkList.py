import urllib, urllib2, sys
import ssl
import json
import MySQLdb as mdb


#常量
curr_page = 1
total_pages = -1
markets = ['sh','sz','hk']
host = 'https://ali-stock.showapi.com'
path = '/stocklist'
method = 'GET'
appcode = 'f86b2760312b41a0b9ef963ceca71b0b'
bodys = {}

#数据库配置
mysql_ip = '106.15.72.40'
mysql_port = '3306'
mysql_user = 'ayesha'
mysql_pass = 'Ayesha_topaz77'
mysql_db = 'ayesha'

#将返回的字符串转换为json对象
json_content = json.loads(content)
#提取全部页数
total_pages = int(json_content['showapi_res_body']['allPages'])
#如果当前请求的页数没有达到全部页数，则当前页+1
if(curr_page < total_pages):
	curr_page = curr_page + 1
#如果当前请求的页数已经达到了上限，切换市场
else:




#with open('result.txt', 'w') as f:
#    f.write(content)


#查询market,page条件下的股票产品
def requestContent(market,page):
	url = host + path + '?' + 'market=' + market + '&' + 'page='+page
	request = urllib2.Request(url)
	request.add_header('Authorization', 'APPCODE ' + appcode)
	ctx = ssl.create_default_context()
	ctx.check_hostname = False
	ctx.verify_mode = ssl.CERT_NONE
	response = urllib2.urlopen(request, context=ctx)
	content = response.read()
	return content

def saveToDB(stock_json):
	with mdb.connect(mysql_ip, mysql_port,mysql_user, mysql_pass,mysql_db) as con:
		cur = conn.cursor()
		code = stock_json['code']
		record = cur.execute('select * from stock where code = %s' , [code]).fetchone();

