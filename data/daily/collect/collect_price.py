#coding=utf-8
import os
import urllib2
from itertools import islice
import datetime
import db.db as db
import db.stock as stock
import db.stock_price as stock_price
import config



def read_price_file(file_name,market,cursor):
    with open(file_name) as f:
        lines = f.readlines()
        for line in islice(lines, 1, None): 
            save_price(line,market,cursor)
    

def format_value(value,formation):
    value = value.replace('\'','')
    if value == 'None' or value == '':
        value = None
    if formation is not None:
        try:
            value = format(float(value),formation)
        except:
            value = None
    return value


def save_price(stock_line,market,cursor):
    contents = stock_line.split(',')

    #日期0,股票代码1,名称2,收盘价3,最高价4,最低价5,开盘价6,前收盘7,涨跌额8,涨跌幅9,换手率10,成交量11,成交金额12,总市值13,流通市值14,成交笔数15
    #最低价5
    min_price = format_value(contents[5],'0.2f')
        
    #成交量11
    trade_num = format_value(contents[11],'0.4f')

    #成交金额12
    trade_money = format_value(contents[12],'0.4f')

    #收盘价3
    close_price = format_value(contents[3],'0.2f')

    #开盘价6
    open_price = format_value(contents[6],'0.2f')

    #股票代码
    code = format_value(contents[1],None)

    #最高价4
    max_price = format_value(contents[4],'0.2f')

    #日期
    date = format_value(contents[0],None)

    #前收盘7
    last_close_price = format_value(contents[7],'0.2f')

    #涨跌额8
    increase = format_value(contents[8],'0.2f')

    #涨跌幅9
    increase_rate = format_value(contents[9],'0.4f')

    #换手率10
    turnover_rate = format_value(contents[10],'0.4f')

    #总市值13
    total_value = format_value(contents[13],'0.4f')
    
    #流通市值14
    circulation_value = format_value(contents[14],'0.4f')

    params = [min_price,market,trade_num,trade_money,close_price,open_price,
            code,max_price,date,last_close_price,increase,increase_rate,
            turnover_rate,total_value,circulation_value,
            min_price,market,trade_num,trade_money,close_price,open_price,
            max_price,last_close_price,increase,increase_rate,
            turnover_rate,total_value,circulation_value]

    print('refreshing stock price ' + code + ' ' + date)
    stock_price.refresh_stock_price(params,cursor)


def download_price_file(begin,end,code,market_code):
    url = config.PRICE_HOST + '?code=' + bytes(market_code) + bytes(code) + '&start=' + begin + '&end=' + end 
    f = urllib2.urlopen(url) 
    data = f.read() 
    with open(code + '.csv', "w") as file:     
        file.write(data)


def collect_price(begin,end):
    conn,cursor = db.db_connect()
    enddate = datetime.datetime(int(end[0:4]),int(end[5:7]),int(end[8:10]))
    begindate = datetime.datetime(int(begin[0:4]),int(begin[5:7]),int(begin[8:10]))

    begin = begindate.strftime('%Y%m%d')
    end = enddate.strftime('%Y%m%d')
    for market in config.MARKETS:
        code_list = stock.get_stock_by_market(market,cursor)
        for code in code_list:
            if market == 'sh':
                download_price_file(begin,end,code,0)
            else:
                download_price_file(begin,end,code,1)
            read_price_file(code + '.csv',market,cursor)
            os.remove(code + '.csv')
    conn.commit()
    db.db_close(conn,cursor)


if __name__ == '__main__':
    collect_price('2017-08-14','2017-08-14')