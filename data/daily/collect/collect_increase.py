#coding=utf-8
import numpy as np
import config
import math
import decimal
import datetime
import db.db as db
import db.stock as stock
import db.stock_price as stock_price
import db.stock_increase as stock_increase


def calculate_stock_increase(begin,end,code,market,cursor):
    stock_history_list = stock_price.get_stock_increase_calculation_set(begin,end,code,cursor)
    for stock_history in stock_history_list:
        date = stock_history[8]

        if date < begin or date > end:
            continue

        #计算inc_day
        data_set_x_day = get_data_set_x(stock_history_list,date,2)
        data_set_y_day = get_data_set_y(stock_history_list,date,2)
        inc_day = calculate_increase(data_set_y_day[0],data_set_y_day[len(data_set_y_day)-1])

        data_set_x_30 = get_data_set_x(stock_history_list,date,30)
        data_set_y_30 = get_data_set_y(stock_history_list,date,30)
        inc_30 = None
        fit_inc_30_1 = None
        fit_inc_30_2 = None
        if len(data_set_x_30) == 30 and len(data_set_y_30) == 30:
            inc_30 = calculate_increase(data_set_y_30[0],data_set_y_30[len(data_set_y_30)-1])
            fit_inc_30_1 = calculate_poly_fit(data_set_x_30,data_set_y_30,1)
            fit_inc_30_2 = calculate_poly_fit(data_set_x_30,data_set_y_30,2)

        data_set_x_90 = get_data_set_x(stock_history_list,date,90)
        data_set_y_90 = get_data_set_y(stock_history_list,date,90)
        inc_90 = None
        fit_inc_90_1 = None
        fit_inc_90_2 = None
        if len(data_set_x_90) == 90 and len(data_set_y_90) == 90:
            inc_90 = calculate_increase(data_set_y_90[0],data_set_y_90[len(data_set_y_90)-1])
            fit_inc_90_1 = calculate_poly_fit(data_set_x_90,data_set_y_90,1)
            fit_inc_90_2 = calculate_poly_fit(data_set_x_90,data_set_y_90,2)

        data_set_x_180 = get_data_set_x(stock_history_list,date,180)
        data_set_y_180 = get_data_set_y(stock_history_list,date,180)
        inc_180 = None
        fit_inc_180_1 = None
        fit_inc_180_2 = None
        if len(data_set_x_180) == 180 and len(data_set_y_180) == 180:
            inc_180 = calculate_increase(data_set_y_180[0],data_set_y_180[len(data_set_y_180)-1])
            fit_inc_180_1 = calculate_poly_fit(data_set_x_180,data_set_y_180,1)
            fit_inc_180_2 = calculate_poly_fit(data_set_x_180,data_set_y_180,2)

        data_set_x_360 = get_data_set_x(stock_history_list,date,360)
        data_set_y_360 = get_data_set_y(stock_history_list,date,360)
        inc_360 = None
        fit_inc_360_1 = None
        fit_inc_360_2 = None
        if len(data_set_x_360) == 360 and len(data_set_y_360) == 360:
            inc_360 = calculate_increase(data_set_y_360[0],data_set_y_360[len(data_set_y_360)-1])
            fit_inc_360_1 = calculate_poly_fit(data_set_x_360,data_set_y_360,1)
            fit_inc_360_2 = calculate_poly_fit(data_set_x_360,data_set_y_360,2)





        params = [date,code,inc_day,inc_30,inc_90,inc_180,inc_360,fit_inc_30_1,
            fit_inc_30_2,fit_inc_90_1,fit_inc_90_2,fit_inc_180_1,fit_inc_180_2,
            fit_inc_360_1,fit_inc_360_2,inc_day,inc_30,inc_90,inc_180,inc_360,
            fit_inc_30_1,fit_inc_30_2,fit_inc_90_1,fit_inc_90_2,fit_inc_180_1,
            fit_inc_180_2,fit_inc_360_1,fit_inc_360_2]

        print('refreshing stock increase ' + code + ' ' + date)
        stock_increase.refresh_stock_increase(params,cursor)

def calculate_increase(prev_value,curr_value):
    if prev_value == 0:
        return None
    return format((curr_value - prev_value) / prev_value,'0.4f')

#入参为顺序数组
#eg:
#dataX:[1,2,3,4,5]
#dataY:[10.00,10.12,10.22,9.98,10.04]
def calculate_poly_fit(dataX,dataY,degree):
    params = np.polyfit(dataX, dataY, degree)
    level = len(params)
    x = dataX[-1]
    y = 0;
    for i in range(0, level, 1):
        y = y + params[i]*math.pow(x * 2-1, level - i - 1)
    prev_value = dataY[-1]
    return format((y - prev_value) / prev_value , '0.4f')

#这里获取的是倒转数组，因此需要reverse
def get_data_set_x(stock_history_list,end,peroid):
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
                return reverse_array(data_set)
    return reverse_array(data_set)

def get_data_set_y(stock_history_list,end,peroid):
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
                return reverse_array(data_set)
    return reverse_array(data_set)


def reverse_array(arr):
    reverse_arr = []
    for i in range(len(arr)-1,-1,-1):
        reverse_arr.append(arr[i])
    return reverse_arr


def collect_increase(begin,end):
    conn,cursor = db.db_connect()
    for market in config.MARKETS:
        code_list = stock.get_stock_by_market(market,cursor)
        for code in code_list:
            calculate_stock_increase(begin,end,code,market,cursor)
    conn.commit()
    db.db_close(conn,cursor)


if __name__ == '__main__':
    collect_increase('2017-09-13','2017-09-13')