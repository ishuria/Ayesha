#coding=utf-8
import numpy as np
import MySQLdb as mdb
import stock_sql
import config
import math
import decimal
import datetime


markets = ['sh','sz']


def processIncrease(begin,end):
	for market in markets:
		code_list = getCodeList(market)
		line_num = 0  
		for code in code_list:
			processStockIncrease(begin,end,code,market)

def processStockIncrease(begin,end,code,market):
	conn = mdb.connect(host=config.mysql_ip, port=config.mysql_port,user=config.mysql_user,passwd=config.mysql_pass,db=config.mysql_db,charset='utf8')
	cursor = conn.cursor()

	stock_history_list = requestStockHistory(begin,end,code,cursor)
	stock_future_list = requestStockFuture(begin,end,code,cursor)
	for stock_history in stock_history_list:
		date = stock_history[8]

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















		cursor.execute(''.join(['SELECT count(1)', 
							'FROM ',
								'stock_train_data ',
							'WHERE ',
								'stock_train_data.`code` = %s AND stock_train_data.date= %s ']), [code, date])
		result = cursor.fetchone()
		count = result[0]
		#如果有记录，更新
		if count == 1:
			print('update increase code = ' + code + ',date = ' + date)
			cursor.execute(''.join(['UPDATE stock_train_data set ',
										'stock_train_data.inc_30 = %s, ',
										'stock_train_data.inc_90 = %s, ',
										'stock_train_data.inc_180 = %s, ',
										'stock_train_data.inc_360 = %s, ',
										'stock_train_data.turn_30 = %s, ',
										'stock_train_data.turn_90 = %s, '
										'stock_train_data.turn_180 = %s, ',
										'stock_train_data.turn_360 = %s, ',
										'stock_train_data.trade_money_30 = %s, ',
										'stock_train_data.trade_money_90 = %s, ',
										'stock_train_data.trade_money_180 = %s, ',
										'stock_train_data.trade_money_360 = %s, ',
										'stock_train_data.trade_num_30 = %s, ',
										'stock_train_data.trade_num_90 = %s, ',
										'stock_train_data.trade_num_180 = %s, ',
										'stock_train_data.trade_num_360 = %s, ',
										'stock_train_data.future_inc_30 = %s, ',
										'stock_train_data.future_inc_90 = %s, ',
										'stock_train_data.future_inc_180 = %s, ',
										'stock_train_data.future_inc_360 = %s, ',
										'stock_train_data.future_price_30 = %s, ',
										'stock_train_data.future_price_90 = %s, ',
										'stock_train_data.future_price_180 = %s, ',
										'stock_train_data.future_price_360 = %s ',
									'WHERE ',
										'stock_train_data.`code` = %s AND stock_train_data.date= %s ']), 
									[inc_30,
									inc_90,
									inc_180,
									inc_360,
									turn_30,
									turn_90,
									turn_180,
									turn_360,
									trade_money_30,
									trade_money_90,
									trade_money_180,
									trade_money_360,
									trade_num_30,
									trade_num_90,
									trade_num_180,
									trade_num_360,
									future_inc_30,
									future_inc_90,
									future_inc_180,
									future_inc_360,
									future_price_30,
									future_price_90,
									future_price_180,
									future_price_360,
									code, date])


		#否则新增数据
		else:
			print('insert increase code = ' + code + ',date = ' + date)
			cursor.execute(''.join(['INSERT INTO stock_train_data ( ',
										'stock_train_data.date, ',
										'stock_train_data.`code`, ',
										'stock_train_data.inc_30, ',
										'stock_train_data.inc_90, ',
										'stock_train_data.inc_180, ',
										'stock_train_data.inc_360, ',
										'stock_train_data.turn_30, ',
										'stock_train_data.turn_90, ',
										'stock_train_data.turn_180, ',
										'stock_train_data.turn_360, ',
										'stock_train_data.trade_money_30, ',
										'stock_train_data.trade_money_90, ',
										'stock_train_data.trade_money_180, ',
										'stock_train_data.trade_money_360, ',
										'stock_train_data.trade_num_30, ',
										'stock_train_data.trade_num_90, ',
										'stock_train_data.trade_num_180, ',
										'stock_train_data.trade_num_360, ',
										'stock_train_data.future_inc_30, ',
										'stock_train_data.future_inc_90, ',
										'stock_train_data.future_inc_180, ',
										'stock_train_data.future_inc_360, ',
										'stock_train_data.future_price_30, ',
										'stock_train_data.future_price_90, ',
										'stock_train_data.future_price_180, ',
										'stock_train_data.future_price_360 ',
									') ',
									'VALUES ',
										'( ',
											'%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s,%s ,%s,%s ,%s,%s ,%s,%s,%s,%s,%s,%s,%s,%s ',
										')']), 
									[date,code,
									inc_30,
									inc_90,
									inc_180,
									inc_360,
									turn_30,
									turn_90,
									turn_180,
									turn_360,
									trade_money_30,
									trade_money_90,
									trade_money_180,
									trade_money_360,
									trade_num_30,
									trade_num_90,
									trade_num_180,
									trade_num_360,
									future_inc_30,
									future_inc_90,
									future_inc_180,
									future_inc_360,
									future_price_30,
									future_price_90,
									future_price_180,
									future_price_360])


	conn.commit()
	cursor.close()
	conn.close()
	return None

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

def requestStockHistory(begin,end,code,cursor):
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



def requestStockFuture(begin,end,code,cursor):
	stock_future_list = []

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
									'AND date >= %s ',
									'ORDER BY ',
										'date ASC ',
									'LIMIT 0, ',
									'%s ',
								') t ',
							'ORDER BY ',
								'date DESC ']), [code,begin,diff + 380])

	results = cursor.fetchall()
	for result in results:
		stock_future_list.append(result)
	return stock_future_list


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

def reverse(arr):
	reverse_arr = []
	for i in range(len(arr)-1,-1,-1):
		reverse_arr.append(arr[i])
	return reverse_arr

if __name__ == '__main__':
	#print(reverse([1,2,3,4,5]))
	processIncrease('2010-01-01','2017-08-09')
	'''
	begin = '2017-07-01'
	end = '2017-08-09'
	enddate = datetime.datetime(int(end[0:4]),int(end[5:7]),int(end[8:10]))
	begindate = datetime.datetime(int(begin[0:4]),int(begin[5:7]),int(begin[8:10]))
	print((enddate-begindate).days)
	'''
	#processStockIncrease('2016-01-01','2017-08-09','600000','sh')
	#print(calcPolyfit([1,2,4],[1,2,3],2))
	#getDataSetX([1,2,3,4,5],5,5)