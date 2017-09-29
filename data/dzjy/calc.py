# -*- coding: UTF-8 -*-  
import config
import MySQLdb as mdb



TOTAL = 1000000

conn = None
cursor = None

def calc(code,begin,end):
	left = TOTAL

	#获取预测价与收盘价
	cursor.execute(''.join([
            '        SELECT ',
			'			t.`code`, ',
			'			t.date, ',
			'			t.est_price_30, ',
			'			t.future_price_30, ',
			'			d.fq_close_price ',
			'		FROM ',
			'			stock_est_data t inner join stock_history d on d.`code` = t.`code` and d.date = t.date',
			'		WHERE ',
			'			t.`code` = %s ',
			'		AND t.date >= %s ',
			'		AND t.date <= %s ',
			'		AND t.est_price_30 is not null ',
			'		AND t.future_price_30 is not null ',
			'		AND d.fq_close_price is not null ',
			'		ORDER BY ',
			'			t.date ASC '
		]) , [code,begin,end])
	results = cursor.fetchall()

	profit = 0

	cost_list = []

	for i in range(len(results)):
		result = results[i]
		est_price_30 = float(result[2])
		future_price_30 = float(result[3])
		fq_close_price = float(result[4])


		if est_price_30 > fq_close_price:
			if left > fq_close_price * 100:
				left -= fq_close_price * 100
				#profit += ( future_price_30 - fq_close_price ) * 100
				cost = []
				cost.append(fq_close_price)
				cost.append(100)
				cost_list.append(cost)
			else:
				pass
		else:
			for cost in cost_list:
				last_close_price = cost[0]
				last_num = cost[1]
				left += last_num * fq_close_price
				profit += (fq_close_price - last_close_price)*last_num
			cost_list = []
			#print(len(cost_list))


	for cost in cost_list:
		last_close_price = cost[0]
		last_num = cost[1]
		left += last_num * fq_close_price
		profit += (fq_close_price - last_close_price)*last_num
	cost_list = []
	#print(len(cost_list))

	conn.commit()

	print('cost = '+ str(left))
	print('profit = ' + str(profit))
	return None

def db_connect():
    global conn
    global cursor
    conn = mdb.connect(host=config.mysql_ip, port=config.mysql_port,user=config.mysql_user,passwd=config.mysql_pass,db=config.mysql_db,charset='utf8')
    cursor = conn.cursor()

def db_close():
    cursor.close()
    conn.close()

if __name__ == '__main__':
	db_connect()
	calc('600000','2017-01-01','2017-12-31')
	db_close()