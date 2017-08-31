#coding=utf-8
import numpy as np
import MySQLdb as mdb
import stock_sql
import config
import math
import decimal
import datetime


markets = ['sh','sz']

conn = None
cursor = None

def processIncrease(begin,end):
	global conn
	global cursor
	#开启数据库连接
	conn = mdb.connect(host=config.mysql_ip, port=config.mysql_port,user=config.mysql_user,passwd=config.mysql_pass,db=config.mysql_db,charset='utf8')
	cursor = conn.cursor()
	for market in markets:
		code_list = getCodeList(market)
		for code in code_list:
			processStockIncrease(begin,end,code,market)
	cursor.close()
	conn.close()



def processStockIncrease(begin,end,code,market):
	global conn
	global cursor
	stock_history_list = requestStockHistory(begin,end,code)
	for stock_history in stock_history_list:
		date = stock_history[8]

		if date < begin or date > end:
			continue

		#计算inc_day
		data_set_x_day = getDataSetX(stock_history_list,date,2)
		data_set_y_day = getDataSetY(stock_history_list,date,2)
		inc_day = calcIncrease(data_set_y_day[0],data_set_y_day[len(data_set_y_day)-1])

		data_set_x_30 = getDataSetX(stock_history_list,date,30)
		data_set_y_30 = getDataSetY(stock_history_list,date,30)
		inc_30 = None
		fit_inc_30_1 = None
		fit_inc_30_2 = None
		if len(data_set_x_30) == 30 and len(data_set_y_30) == 30:
			inc_30 = calcIncrease(data_set_y_30[0],data_set_y_30[len(data_set_y_30)-1])
			fit_inc_30_1 = calcPolyfit(data_set_x_30,data_set_y_30,1)
			fit_inc_30_2 = calcPolyfit(data_set_x_30,data_set_y_30,2)

		data_set_x_90 = getDataSetX(stock_history_list,date,90)
		data_set_y_90 = getDataSetY(stock_history_list,date,90)
		inc_90 = None
		fit_inc_90_1 = None
		fit_inc_90_2 = None
		if len(data_set_x_90) == 90 and len(data_set_y_90) == 90:
			inc_90 = calcIncrease(data_set_y_90[0],data_set_y_90[len(data_set_y_90)-1])
			fit_inc_90_1 = calcPolyfit(data_set_x_90,data_set_y_90,1)
			fit_inc_90_2 = calcPolyfit(data_set_x_90,data_set_y_90,2)

		data_set_x_180 = getDataSetX(stock_history_list,date,180)
		data_set_y_180 = getDataSetY(stock_history_list,date,180)
		inc_180 = None
		fit_inc_180_1 = None
		fit_inc_180_2 = None
		if len(data_set_x_180) == 180 and len(data_set_y_180) == 180:
			inc_180 = calcIncrease(data_set_y_180[0],data_set_y_180[len(data_set_y_180)-1])
			fit_inc_180_1 = calcPolyfit(data_set_x_180,data_set_y_180,1)
			fit_inc_180_2 = calcPolyfit(data_set_x_180,data_set_y_180,2)

		data_set_x_360 = getDataSetX(stock_history_list,date,360)
		data_set_y_360 = getDataSetY(stock_history_list,date,360)
		inc_360 = None
		fit_inc_360_1 = None
		fit_inc_360_2 = None
		if len(data_set_x_360) == 360 and len(data_set_y_360) == 360:
			inc_360 = calcIncrease(data_set_y_360[0],data_set_y_360[len(data_set_y_360)-1])
			fit_inc_360_1 = calcPolyfit(data_set_x_360,data_set_y_360,1)
			fit_inc_360_2 = calcPolyfit(data_set_x_360,data_set_y_360,2)


		cursor.execute(''.join(['SELECT count(1)', 
							'FROM ',
								'stock_increase ',
							'WHERE ',
								'stock_increase.`code` = %s AND stock_increase.date= %s ']), [code, date])
		result = cursor.fetchone()
		count = result[0]
		#如果有记录，更新
		if count == 1:
			print('update increase code = ' + code + ',date = ' + date)
			cursor.execute(''.join(['UPDATE stock_increase set ',
										'stock_increase.inc_day = %s, ',
										'stock_increase.inc_30 = %s, ',
										'stock_increase.inc_90 = %s, ',
										'stock_increase.inc_180 = %s, ',
										'stock_increase.inc_360 = %s, ',
										'stock_increase.fit_inc_30_1 = %s, ',
										'stock_increase.fit_inc_30_2 = %s, '
										'stock_increase.fit_inc_90_1 = %s, ',
										'stock_increase.fit_inc_90_2 = %s, ',
										'stock_increase.fit_inc_180_1 = %s, ',
										'stock_increase.fit_inc_180_2 = %s, ',
										'stock_increase.fit_inc_360_1 = %s, ',
										'stock_increase.fit_inc_360_2 = %s ',
									'WHERE ',
										'stock_increase.`code` = %s AND stock_increase.date= %s ']), [inc_day,inc_30,inc_90,inc_180,inc_360,fit_inc_30_1,fit_inc_30_2,fit_inc_90_1,fit_inc_90_2,fit_inc_180_1,fit_inc_180_2,fit_inc_360_1,fit_inc_360_2,code, date])


		#否则新增数据
		else:
			print('insert increase code = ' + code + ',date = ' + date)
			cursor.execute(''.join(['INSERT INTO stock_increase ( ',
										'stock_increase.date, ',
										'stock_increase.`code`, ',
										'stock_increase.inc_day, ',
										'stock_increase.inc_30, ',
										'stock_increase.inc_90, ',
										'stock_increase.inc_180, ',
										'stock_increase.inc_360, ',
										'stock_increase.fit_inc_30_1, ',
										'stock_increase.fit_inc_30_2, '
										'stock_increase.fit_inc_90_1, ',
										'stock_increase.fit_inc_90_2, ',
										'stock_increase.fit_inc_180_1, ',
										'stock_increase.fit_inc_180_2, ',
										'stock_increase.fit_inc_360_1, ',
										'stock_increase.fit_inc_360_2 ',
									') ',
									'VALUES ',
										'( ',
											'%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s,%s ,%s,%s ,%s,%s ,%s ',
										')']), [date,code,inc_day,inc_30,inc_90,inc_180,inc_360,fit_inc_30_1,fit_inc_30_2,fit_inc_90_1,fit_inc_90_2,fit_inc_180_1,fit_inc_180_2,fit_inc_360_1,fit_inc_360_2])





	conn.commit()
	return None

def calcIncrease(prev_value,curr_value):
	if prev_value == 0:
		return None
	return format((curr_value - prev_value) / prev_value,'0.4f')

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

def requestStockHistory(begin,end,code):
	global conn
	global cursor
	stock_history_list = []

	enddate = datetime.datetime(int(end[0:4]),int(end[5:7]),int(end[8:10]))
	begindate = datetime.datetime(int(begin[0:4]),int(begin[5:7]),int(begin[8:10]))
	diff = (enddate-begindate).days


	cursor.execute(''.join(['SELECT ',
								'* ',
							'FROM ',
								'( ',
									'SELECT ',
										'stock_history.min_price, ',
										'stock_history.market, ',
										'stock_history.trade_num, ',
										'stock_history.trade_money, ',
										'stock_history.close_price, ',
										'stock_history.open_price, ',
										'stock_history.`code`, ',
										'stock_history.max_price, ',
										'stock_history.date, ',
										'stock_history.last_close_price, ',
										'stock_history.increase, ',
										'stock_history.increase_rate, ',
										'stock_history.turnover_rate, ',
										'stock_history.total_value, ',
										'stock_history.circulation_value, ',
										'stock_history.fq_close_price ',
									'FROM ',
										'stock_history ',
									'WHERE ',
										'stock_history.`code` = %s ',
									'AND stock_history.fq_close_price IS NOT NULL ',
									'AND date <= %s ',
									'ORDER BY ',
										'date DESC ',
									'LIMIT 0, ',
									'%s ',
								') t ',
							'ORDER BY ',
								'date ASC ']), [code,end,diff + 380])

	results = cursor.fetchall()
	for result in results:
		stock_history_list.append(result)

	return stock_history_list


def getCodeList(market):
	global conn
	global cursor

	stock_list = []
	cursor.execute(stock_sql.stock_market_select_sql , [market])
	results = cursor.fetchall()
	for result in results:
		stock_list.append(result[6])

	conn.commit()
	return stock_list

def reverse(arr):
	reverse_arr = []
	for i in range(len(arr)-1,-1,-1):
		reverse_arr.append(arr[i])
	return reverse_arr

if __name__ == '__main__':
	processIncrease('2015-08-01','2017-08-09')