#coding=utf-8
import sys
import config
import MySQLdb as mdb
import subprocess
import datetime
import db.db as db
import db.stock as stock
import multiprocessing

def start_est_process(command):
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in p.stdout.readlines():
        print line,
    retval = p.wait()

if __name__ == '__main__':
    conn,cursor = db.db_connect()
    today = datetime.date.today().strftime("%Y-%m-%d")

    processes = []

    if len(sys.argv) == 1:
        date = today
        for market in config.MARKETS:
            code_list = stock.get_stock_by_market(market,cursor)
            #每批次起config.EST_PROCESS_NUM个进程

            pool = multiprocessing.Pool(processes=config.EST_PROCESS_NUM)
            result = []

            for code in code_list:
                command = 'python -m daily.estimate.est' + ' ' + code + ' ' + str(30) + ' ' + '30' + ' ' + date
                p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                result.append(pool.apply_async(func, (msg, )))

            pool.close()
            pool.join()

            for res in result:
                print ":::", res.get()

    if len(sys.argv) == 2 and sys.argv[1] != None:
        date = sys.argv[1]
        for market in config.MARKETS:
            code_list = stock.get_stock_by_market(market,cursor)


            pool = multiprocessing.Pool(processes=config.EST_PROCESS_NUM)
            result = []

            for i in xrange(len(code_list)):
                code = code_list[i]
                command = 'python -m daily.estimate.est' + ' ' + code + ' ' + str(30) + ' ' + '30' + ' ' + date
                
                result.append(pool.apply_async(start_est_process, (command, )))

            pool.close()
            pool.join()

            for res in result:
                print ":::", res.get()

    db.db_close(conn,cursor)
    '''
    if len(sys.argv) == 2 and sys.argv[1] != None:
        date = sys.argv[1]
        for market in config.MARKETS:
            code_list = stock.get_stock_by_market(market,cursor)
            for code in code_list:
                command = 'python -m daily.estimate.est' + ' ' + code + ' ' + str(30) + ' ' + '30' + ' ' + date
                p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                print(code)
                #for line in p.stdout.readlines():
                #    print line,
                #retval = p.wait()
	db.db_close(conn,cursor)
    '''