#coding=utf-8
import numpy as np
import MySQLdb as mdb
import stock_sql
import config
import math



markets = ['sh','sz']



def processIncrease(begin,end):
	for market in markets:
		code_list = getCodeList(market)
		line_num = 0  
		for code in code_list:
			processStockIncrease(begin,end,code,market)



def processStockIncrease(begin,end,code,market):
	stock_history_list = requestStockHistory(begin,end,code)
	for stock_history in stock_history_list:
		date = stock_history[8]
		#计算inc_day
		data_set_x_day = getDataSetX(stock_history_list,date,1)
		data_set_y_day = getDataSetY(stock_history_list,date,1)
		inc_day = calcIncrease(data_set_y_day[0],data_set_y_day[len(data_set_y_day)-1])

		data_set_x_30 = getDataSetX(stock_history_list,date,30)
		print(data_set_x_30)
		data_set_y_30 = getDataSetY(stock_history_list,date,30)
		print(data_set_y_30)

		if len(data_set_x_30) == 30 and len(data_set_y_30) == 30:
			inc_30 = calcIncrease(data_set_y_30[0],data_set_y_30[len(data_set_y_30)-1])
			fit_inc_30_1 = calcPolyfit(data_set_x_30,data_set_y_30,1)
			fit_inc_30_2 = calcPolyfit(data_set_x_30,data_set_y_30,2)

		data_set_x_90 = getDataSetX(stock_history_list,date,90)
		data_set_y_90 = getDataSetY(stock_history_list,date,90)
		if len(data_set_x_90) == 90 and len(data_set_y_90) == 90:
			inc_90 = calcIncrease(data_set_y_90[0],data_set_y_90[len(data_set_y_90)-1])
			fit_inc_90_1 = calcPolyfit(data_set_x_90,data_set_y_90,1)
			fit_inc_90_2 = calcPolyfit(data_set_x_90,data_set_y_90,2)

		data_set_x_180 = getDataSetX(stock_history_list,date,180)
		data_set_y_180 = getDataSetY(stock_history_list,date,180)
		if len(data_set_x_180) == 180 and len(data_set_y_180) == 180:
			inc_180 = calcIncrease(data_set_y_180[0],data_set_y_180[len(data_set_y_180)-1])
			fit_inc_180_1 = calcPolyfit(data_set_x_180,data_set_y_180,1)
			fit_inc_180_2 = calcPolyfit(data_set_x_180,data_set_y_180,2)

		data_set_x_360 = getDataSetX(stock_history_list,date,360)
		data_set_y_360 = getDataSetY(stock_history_list,date,360)
		if len(data_set_x_360) == 360 and len(data_set_y_360) == 360:
			inc_360 = calcIncrease(data_set_y_360[0],data_set_y_360[len(data_set_y_360)-1])
			fit_inc_360_1 = calcPolyfit(data_set_x_360,data_set_y_360,1)
			fit_inc_360_2 = calcPolyfit(data_set_x_360,data_set_y_360,2)

	'''
	inc_day
	inc_30
	inc_90
	inc_180
	inc_360
	fit_inc_30_1
	fit_inc_90_1
	fit_inc_180_1
	fit_inc_360_1
	fit_inc_30_2
	fit_inc_90_2
	fit_inc_180_2
	fit_inc_360_2
	'''
	return None

def calcIncrease(prev_value,curr_value):
	return format((curr_value - prev_value) / prev_value,'0.4f')

def calcPolyfit(dataX,dataY,degree):
	params = np.polyfit(dataX, dataY, degree)
	level = len(params)
	x = dataX[len(dataX)-1]
	y = 0;
	for i in range(0, level, 1):
		y = y + params[i]*math.pow(x, level - i - 1)
	return y

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
			if peroid < 0:
				return None
	return data_set

def getDataSetY(stock_history_list,end,peroid):
	data_set = []
	start_collect = False
	for i in range(len(stock_history_list)-1,-1,-1):
		date = stock_history_list[i][8]
		if date == end:
			start_collect = True
		if start_collect:
			data_set.append(stock_history_list[i][4])
			peroid = peroid - 1
			if peroid < 0:
				return None
	return data_set

def requestStockHistory(begin,end,code):
	conn = mdb.connect(host=config.mysql_ip, port=config.mysql_port,user=config.mysql_user,passwd=config.mysql_pass,db=config.mysql_db,charset='utf8')
	cursor = conn.cursor()

	stock_history_list = []
	cursor.execute(''.join(['SELECT ',
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
								'stock_history.circulation_value ',
							'FROM ',
								'stock_history ',
							'WHERE ',
								'stock_history.`code` = %s ']), [code])


	results = cursor.fetchall()
	for result in results:
		stock_history_list.append(result)

	conn.commit()
	cursor.close()
	conn.close()
	return stock_history_list


def getCodeList(market):
	conn = mdb.connect(host=config.mysql_ip, port=config.mysql_port,user=config.mysql_user,passwd=config.mysql_pass,db=config.mysql_db,charset='utf8')
	cursor = conn.cursor()

	stock_list = []
	cursor.execute(stock_sql.stock_market_select_sql , [market])
	results = cursor.fetchall()
	for result in results:
		stock_list.append(result[6])

	conn.commit()
	cursor.close()
	conn.close()
	return stock_list


if __name__ == '__main__':
	processStockIncrease('2000-01-01','2017-08-09','600000','sh')
	#print(calcPolyfit([1,2,4],[1,2,3],2))
	#getDataSetX([1,2,3,4,5],5,5)