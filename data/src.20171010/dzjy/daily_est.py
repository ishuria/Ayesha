#coding=utf-8
import sys
import config
import MySQLdb as mdb
import subprocess
import datetime

#市场
markets = ['sh']

conn = None
cursor = None

def getCodeList(market):
    stock_list = []
    cursor.execute(''.join(['SELECT ',
                                'stock.stockType, ',
                                'stock.market, ',
                                'stock.`name`, ',
                                'stock.state, ',
                                'stock.currcapital, ',
                                'stock.profit_four, ',
                                'stock.`code`, ',
                                'stock.totalcapital, ',
                                'stock.mgjzc, ',
                                'stock.pinyin, ',
                                'stock.listing_date, ',
                                'stock.ct ',
                            'FROM ',
                                'stock ',
                            'WHERE ',
                                'stock.market = %s ']) , [market])
    results = cursor.fetchall()
    for result in results:
        stock_list.append(result[6])
    return stock_list

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
    today = datetime.date.today().strftime("%Y-%m-%d")
    if len(sys.argv) == 1:
        date = today
        for market in markets:
            code_list = getCodeList(market)
            for code in code_list:
                command = 'python train_dzjy.py' + ' ' + code + ' ' + str(80) + ' ' + str(30) + ' ' + '30' + ' ' + date
                p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                for line in p.stdout.readlines():
                    print line,
                retval = p.wait()
    if len(sys.argv) == 2 and sys.argv[1] != None:
        date = sys.argv[1]
        for market in markets:
            code_list = getCodeList(market)
            for code in code_list:
                command = 'python train_dzjy.py' + ' ' + code + ' ' + str(80) + ' ' + str(30) + ' ' + '30' + ' ' + date
                p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                for line in p.stdout.readlines():
                    print line,
                retval = p.wait()
	db_close()