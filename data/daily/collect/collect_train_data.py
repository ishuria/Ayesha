#coding=utf-8
import numpy as np
import config
import math
import decimal
import datetime

import db.db as db
import db.stock as stock
import db.stock_price as stock_price
import db.stock_train_data as stock_train_data





def collect_stock_train_data(begin,end,code,market,cursor):

    stock_history_list = stock_price.get_stock_increase_calculation_set(begin,end,code,cursor)

    stock_future_list = stock_price.get_stock_future_calculation_set(begin,end,code,cursor)


    for stock_history in stock_history_list:
        date = stock_history[8]
        fq_close_price = stock_history[15]

        if date < begin or date > end:
            continue

        #计算inc
        data_set_x_30 = getDataSetX(stock_history_list,date,30)
        data_set_y_30 = getDataSetY(stock_history_list,date,30)
        inc_30 = None

        data_set_x_90 = getDataSetX(stock_history_list,date,90)
        data_set_y_90 = getDataSetY(stock_history_list,date,90)
        inc_90 = None

        data_set_x_180 = getDataSetX(stock_history_list,date,180)
        data_set_y_180 = getDataSetY(stock_history_list,date,180)
        inc_180 = None

        data_set_x_360 = getDataSetX(stock_history_list,date,360)
        data_set_y_360 = getDataSetY(stock_history_list,date,360)
        inc_360 = None

        if len(data_set_x_30) == 30 and len(data_set_y_30) == 30:
            inc_30 = calcIncrease(data_set_y_30[0],data_set_y_30[len(data_set_y_30)-1])

        if len(data_set_x_90) == 90 and len(data_set_y_90) == 90:
            inc_90 = calcIncrease(data_set_y_90[0],data_set_y_90[len(data_set_y_90)-1])

        if len(data_set_x_180) == 180 and len(data_set_y_180) == 180:
            inc_180 = calcIncrease(data_set_y_180[0],data_set_y_180[len(data_set_y_180)-1])

        if len(data_set_x_360) == 360 and len(data_set_y_360) == 360:
            inc_360 = calcIncrease(data_set_y_360[0],data_set_y_360[len(data_set_y_360)-1])
        
        #计算turn_over
        turn_30 = None
        turn_set_30 = []

        trade_money_30 = None
        trade_money_set_30 = []

        trade_num_30 = None
        trade_num_set_30 = []

        getDataSet(stock_history_list,date,30,trade_num_set_30,trade_money_set_30,turn_set_30)

        if len(turn_set_30) == 30:
            turn_30 = calcAvg(turn_set_30)

        #计算trade_money        
        if len(trade_money_set_30) == 30:
            trade_money_30 = calcAvg(trade_money_set_30)

        #计算trade_num
        if len(trade_num_set_30) == 30:
            trade_num_30 = calcAvg(trade_num_set_30)

        turn_90 = None
        turn_set_90 = []

        trade_money_90 = None
        trade_money_set_90 = []

        trade_num_90 = None
        trade_num_set_90 = []

        getDataSet(stock_history_list,date,90,trade_num_set_90,trade_money_set_90,turn_set_90)

        if len(turn_set_90) == 90:
            turn_90 = calcAvg(turn_set_90)

        if len(trade_money_set_90) == 90:
            trade_money_90 = calcAvg(trade_money_set_90)

        if len(trade_num_set_90) == 90:
            trade_num_90 = calcAvg(trade_num_set_90)
        
        turn_180 = None
        turn_set_180 = []

        trade_money_180 = None
        trade_money_set_180 = []

        trade_num_180 = None
        trade_num_set_180 = []

        getDataSet(stock_history_list,date,180,trade_num_set_180,trade_money_set_180,turn_set_180)

        if len(turn_set_180) == 180:
            turn_180 = calcAvg(turn_set_180)

        if len(trade_money_set_180) == 180:
            trade_money_180 = calcAvg(trade_money_set_180)

        if len(trade_num_set_180) == 180:
            trade_num_180 = calcAvg(trade_num_set_180)

        turn_360 = None
        turn_set_360 = []

        trade_money_360 = None
        trade_money_set_360 = []

        trade_num_360 = None
        trade_num_set_360 = []

        getDataSet(stock_history_list,date,360,trade_num_set_360,trade_money_set_360,turn_set_360)
            
        if len(turn_set_360) == 360:
            turn_360 = calcAvg(turn_set_360)
        
        if len(trade_money_set_360) == 360:
            trade_money_360 = calcAvg(trade_money_set_360)

        if len(trade_num_set_360) == 360:
            trade_num_360 = calcAvg(trade_num_set_360)


        future_inc_30 = None
        future_price_30 = None
        future_inc_set_30 = []
        getFutureDataSet(stock_future_list,date,30,future_inc_set_30)
        if len(future_inc_set_30) == 30:
            future_inc_30 = calcIncrease(future_inc_set_30[0],future_inc_set_30[len(future_inc_set_30)-1])
            future_price_30 = future_inc_set_30[len(future_inc_set_30)-1]

        future_inc_90 = None
        future_price_90 = None
        future_inc_set_90 = []
        getFutureDataSet(stock_future_list,date,90,future_inc_set_90)
        if len(future_inc_set_90) == 90:
            future_inc_90 = calcIncrease(future_inc_set_90[0],future_inc_set_90[len(future_inc_set_90)-1])
            future_price_90 = future_inc_set_90[len(future_inc_set_90)-1]

        future_inc_180 = None
        future_price_180 = None
        future_inc_set_180 = []
        getFutureDataSet(stock_future_list,date,180,future_inc_set_180)
        if len(future_inc_set_180) == 180:
            future_inc_180 = calcIncrease(future_inc_set_180[0],future_inc_set_180[len(future_inc_set_180)-1])
            future_price_180 = future_inc_set_180[len(future_inc_set_180)-1]

        future_inc_360 = None
        future_price_360 = None
        future_inc_set_360 = []
        getFutureDataSet(stock_future_list,date,360,future_inc_set_360)
        if len(future_inc_set_360) == 360:
            future_inc_360 = calcIncrease(future_inc_set_360[0],future_inc_set_360[len(future_inc_set_360)-1])
            future_price_360 = future_inc_set_360[len(future_inc_set_360)-1]

        params = [date,code,
                inc_30,inc_90,inc_180,inc_360,
                turn_30,turn_90,turn_180,turn_360,
                trade_money_30,trade_money_90,trade_money_180,trade_money_360,
                trade_num_30,trade_num_90,trade_num_180,trade_num_360,
                future_inc_30,future_inc_90,future_inc_180,future_inc_360,
                future_price_30,future_price_90,future_price_180,future_price_360,
                inc_30,inc_90,inc_180,inc_360,
                turn_30,turn_90,turn_180,turn_360,
                trade_money_30,trade_money_90,trade_money_180,trade_money_360,
                trade_num_30,trade_num_90,trade_num_180,trade_num_360,
                future_inc_30,future_inc_90,future_inc_180,future_inc_360,
                future_price_30,future_price_90,future_price_180,future_price_360]

        print('refreshing stock train data ' + code + ' ' + date)
        stock_train_data.refresh_stock_train_data(params,cursor)

        #将当前date的price填入之前某一天的future price中
        past_date_set_30 = []
        past_date_30 = None
        getPastDataSet(stock_history_list,date,30,past_date_set_30)
        if len(past_date_set_30) == 30:
            past_date_30 = past_date_set_30[len(past_date_set_30)-1]

        past_date_set_90 = []
        past_date_90 = None
        getPastDataSet(stock_history_list,date,90,past_date_set_90)
        if len(past_date_set_90) == 90:
            past_date_90 = past_date_set_90[len(past_date_set_90)-1]

        past_date_set_180 = []
        past_date_180 = None
        getPastDataSet(stock_history_list,date,180,past_date_set_180)
        if len(past_date_set_180) == 180:
            past_date_180 = past_date_set_180[len(past_date_set_180)-1]

        past_date_set_360 = []
        past_date_360 = None
        getPastDataSet(stock_history_list,date,360,past_date_set_360)
        if len(past_date_set_360) == 360:
            past_date_360 = past_date_set_360[len(past_date_set_360)-1]

        if past_date_30 is not None:
            params = [fq_close_price,code,past_date_30]
            print('update future price 30, code = '+ code+', date = '+date)
            stock_train_data.refresh_future_price(params,cursor)

        if past_date_90 is not None:
            params = [fq_close_price,code,past_date_90]
            print('update future price 90, code = '+ code+', date = '+date)
            stock_train_data.refresh_future_price(params,cursor)

        if past_date_180 is not None:
            params = [fq_close_price,code,past_date_180]
            print('update future price 180, code = '+ code+', date = '+date)
            stock_train_data.refresh_future_price(params,cursor)

        if past_date_360 is not None:
            params = [fq_close_price,code,past_date_360]
            print('update future price 360, code = '+ code+', date = '+date)
            stock_train_data.refresh_future_price(params,cursor)


def calcIncrease(prev_value,curr_value):
    if prev_value == 0:
        return None
    return format((curr_value - prev_value) / prev_value,'0.4f')

def calcAvg(data, total=0.0):
    num = 0
    for item in data: 
        total += item 
        num += 1
    return format(total / num,'0.4f')

#入参为顺序数组
#eg:
#dataX:[1,2,3,4,5]
#dataY:[10.00,10.12,10.22,9.98,10.04]
def calcPolyfit(dataX,dataY,degree):
    params = np.polyfit(dataX, dataY, degree)
    level = len(params)
    x = dataX[len(dataX)-1]
    y = 0;
    for i in range(0, level, 1):
        y = y + params[i]*math.pow(x, level - i - 1)
    prev_value = dataY[0]
    return format((y - prev_value) / prev_value , '0.4f')

#这里获取的是倒转数组，因此需要reverse
def getDataSetX(stock_history_list,end,peroid):
    data_set = []
    start_collect = False
    for i in range(len(stock_history_list)-1,-1,-1):
        date = stock_history_list[i][8]
        if date == end:
            start_collect = True
        if start_collect:
            data_set.append(peroid)
            peroid = peroid - 1
            '''
            修改跳出条件
            '''
            if peroid <= 0:
                return reverse(data_set)
    return reverse(data_set)

def getDataSetY(stock_history_list,end,peroid):
    data_set = []
    start_collect = False
    for i in range(len(stock_history_list)-1,-1,-1):
        date = stock_history_list[i][8]
        if date == end:
            start_collect = True
        if start_collect:
            data_set.append(float(stock_history_list[i][15]))
            peroid = peroid - 1
            '''
            修改跳出条件
            '''
            if peroid <= 0:
                return reverse(data_set)
    return reverse(data_set)

def getDataSet(stock_history_list,end,peroid,trade_num,trade_money,turn):
    start_collect = False
    for i in range(len(stock_history_list)-1,-1,-1):
        date = stock_history_list[i][8]
        if date == end:
            start_collect = True
        if start_collect:
            trade_num.append(float(stock_history_list[i][2]))
            trade_money.append(float(stock_history_list[i][3]))
            turn.append(float(stock_history_list[i][12]))
            peroid = peroid - 1
            '''
            修改跳出条件
            '''
            if peroid <= 0:
                break


def getFutureDataSet(stock_history_list,end,peroid,future):
    start_collect = False
    for i in range(len(stock_history_list)-1,-1,-1):
        date = stock_history_list[i][8]
        if date == end:
            start_collect = True
        if start_collect:
            future.append(float(stock_history_list[i][15]))
            peroid = peroid - 1
            '''
            修改跳出条件
            '''
            if peroid <= 0:
                break


def getPastDataSet(stock_history_list,end,peroid,past):
    start_collect = False
    for i in range(len(stock_history_list)-1,-1,-1):
        date = stock_history_list[i][8]
        if date == end:
            start_collect = True
        if start_collect:
            past.append(date)
            peroid = peroid - 1
            '''
            修改跳出条件
            '''
            if peroid <= 0:
                break



def getCodeList(market):
    global conn
    global cursor
    stock_list = []
    cursor.execute(stock_sql.stock_market_select_sql , [market])
    results = cursor.fetchall()
    for result in results:
        stock_list.append(result[6])
    return stock_list

def reverse(arr):
    reverse_arr = []
    for i in range(len(arr)-1,-1,-1):
        reverse_arr.append(arr[i])
    return reverse_arr


def collect_train_data(begin,end):
    conn,cursor = db.db_connect()
    for market in config.MARKETS:
        code_list = stock.get_stock_by_market(market,cursor)
        for code in code_list:
            collect_stock_train_data(begin,end,code,market,cursor)
            conn.commit()
    db.db_close(conn,cursor)


if __name__ == '__main__':
    collect_train_data('2017-01-05','2017-01-05')