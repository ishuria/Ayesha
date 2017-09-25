# -*- coding: UTF-8 -*-  
import matplotlib.pyplot as plt
import config
import MySQLdb as mdb

conn = None
cursor = None


def db_connect():
    global conn
    global cursor
    conn = mdb.connect(host=config.mysql_ip, port=config.mysql_port,user=config.mysql_user,passwd=config.mysql_pass,db=config.mysql_db,charset='utf8')
    cursor = conn.cursor()

def db_close():
    #关闭数据库连接
    cursor.close()
    conn.close()


def get_draw_data(code,begin,end):
	est_data = []
	real_data = []
	curr_data = []
	indexs = []
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
			'		ORDER BY ',
			'			t.date ASC '
		]) , [code,begin,end])
	results = cursor.fetchall()
	for i in range(len(results)):
		result = results[i]
		indexs.append(i)
		est_data.append(result[2])
		real_data.append(result[3])
		curr_data.append(result[4])
	conn.commit()

	return indexs,est_data,real_data,curr_data



if __name__ == '__main__':
	db_connect()


	indexs,est_data,real_data,curr_data = get_draw_data('600000','2013-01-01','2013-12-01')


	plt.figure()
	plt.plot(indexs, est_data, color='b')
	plt.plot(indexs, real_data,  color='r')
	plt.plot(indexs, curr_data,  color='g')
	plt.show()
	db_close()