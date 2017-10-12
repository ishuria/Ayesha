#coding=utf-8
import sys
import config
import MySQLdb as mdb
import subprocess
import datetime
import db.db as db
import db.stock as stock
import multiprocessing


def start_train_process(command):
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in p.stdout.readlines():
        #don't need these optimazation info.
        if line.find('could speed up CPU computations') < 0:
            print line,
    retval = p.wait()

if __name__ == '__main__':
    conn,cursor = db.db_connect()
    today = datetime.date.today().strftime("%Y-%m-%d")

    if len(sys.argv) == 1:
        date = today
    if len(sys.argv) == 2 and sys.argv[1] != None:
        date = sys.argv[1]

    for market in config.MARKETS:
        code_list = stock.get_stock_by_market(market,cursor)
        pool = multiprocessing.Pool(processes=config.TRAIN_PROCESS_NUM)
        for i in xrange(len(code_list)):
            code = code_list[i]
            command = 'python -m daily.train.train' + ' ' + code + ' ' + str(80) + ' ' + str(30) + ' ' + '30' + ' ' + date
            pool.apply_async(start_train_process, (command, ))
        pool.close()
        pool.join()

	db.db_close(conn,cursor)