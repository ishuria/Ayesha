#coding=utf-8
import db.db as db
import db.stock as stock
import multiprocessing
import datetime
import subprocess
import config


def start_est_process(command):
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in p.stdout.readlines():
        #don't need these optimazation info.
        if line.find('could speed up CPU computations') < 0:
            print line,
    retval = p.wait()


def start_train_process(command):
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in p.stdout.readlines():
        #don't need these optimazation info.
        if line.find('could speed up CPU computations') < 0:
            print line,
    retval = p.wait()


if __name__ == '__main__':
    begin = '2017-03-01'
    end = '2017-04-01'

    today = datetime.date.today().strftime("%Y-%m-%d")

    begindate = datetime.datetime.strptime(begin,'%Y-%m-%d')
    enddate = datetime.datetime.strptime(end,'%Y-%m-%d')

    while begindate <= enddate:

        date = begindate.strftime("%Y-%m-%d")
        conn,cursor = db.db_connect()
        for market in config.MARKETS:
            code_list = stock.get_stock_by_market(market,cursor)
            pool = multiprocessing.Pool(processes=config.TRAIN_PROCESS_NUM)
            for i in xrange(len(code_list)):
                code = code_list[i]
                command = 'python -m daily.train.train' + ' ' + code + ' ' + str(80) + ' ' + str(30) + ' ' + '30' + ' ' + date
                pool.apply_async(start_train_process, (command, ))
            pool.close()
            pool.join()

        for market in config.MARKETS:
            code_list = stock.get_stock_by_market(market,cursor)
            pool = multiprocessing.Pool(processes=config.EST_PROCESS_NUM)
            for i in xrange(len(code_list)):
                code = code_list[i]
                command = 'python -m daily.estimate.est' + ' ' + code + ' ' + str(30) + ' ' + '30' + ' ' + date
                pool.apply_async(start_est_process, (command, ))
            pool.close()
            pool.join()

        conn.commit()
        db.db_close(conn,cursor)
        begindate += datetime.timedelta(days=1)

        clear_process = subprocess.Popen('python -m daily.post.clear_old_model_file', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = clear_process.wait()

