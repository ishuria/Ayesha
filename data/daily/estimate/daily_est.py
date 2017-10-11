#coding=utf-8
import sys
import config
import MySQLdb as mdb
import subprocess
import datetime
import db.db as db
import db.stock as stock


if __name__ == '__main__':
    conn,cursor = db.db_connect()
    today = datetime.date.today().strftime("%Y-%m-%d")
    if len(sys.argv) == 1:
        date = today
        for market in config.MARKETS:
            code_list = getCodeList(market)
            for code in code_list:
                command = 'python est.py' + ' ' + code + ' ' + str(30) + ' ' + '30' + ' ' + date
                p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                for line in p.stdout.readlines():
                    print line,
                retval = p.wait()
    if len(sys.argv) == 2 and sys.argv[1] != None:
        date = sys.argv[1]
        for market in config.MARKETS:
            code_list = getCodeList(market)
            for code in code_list:
                command = 'python est.py' + ' ' + code + ' ' + str(30) + ' ' + '30' + ' ' + date
                p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                for line in p.stdout.readlines():
                    print line,
                retval = p.wait()
	db.db_close(conn,cursor)