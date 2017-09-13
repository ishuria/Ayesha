# -*- coding: UTF-8 -*-  
import numpy as np
import tensorflow as tf
import config
import MySQLdb as mdb
import stock_sql
import datetime

conn = None
cursor = None

input_size=6

rnn_unit=30


#获取测试集
def get_test_data(code,time_step,term,date):
	mean,std,test_x,future_price = None,None,[],None
	#如果当天不是交易日，返回空
	cursor.execute('SELECT count(1) count FROM stock_history WHERE stock_history.`code` = %s AND stock_history.date = %s', [code, date])
	result = cursor.fetchone()
	count = result[0]
	#如果有记录，更新
	if count == 0:
		return mean,std,test_x,future_price

	stock_history_list = []
	stock_price_list = []
	cursor.execute(''.join([
			'SELECT ',
			'	* ',
			'FROM ',
			'	( ',
			'		SELECT ',
			'			t.trade_num, ',
			'			t.trade_money, ',
			'			t.fq_close_price, ',
			'			t.turnover_rate, ',
			'			t.total_value, ',
			'			t.circulation_value, ',
			'			a.future_price_'+term+', ',
			'			t.date ',
			'		FROM ',
			'			stock_history t ',
			'		LEFT JOIN stock_train_data a ON a.`code` = t.`code` ',
			'		AND a.date = t.date ',
			'		WHERE ',
			'			t.date <= %s ',
			'		AND t.`code` = %s ',
			'		AND t.fq_close_price is not null ',
			'		ORDER BY ',
			'			t.date DESC ',
			'		LIMIT 0, ',
			'		' + str(2000) + ' ',
			'	) tt ',
			'ORDER BY ',
			'	tt.date ASC '
		]) , [date,code])
	results = cursor.fetchall()
	for result in results:
		stock_history = []
		stock_price = []
		#trade_num:2
		stock_history.append(float(result[0]))
		#trade_money:3
		stock_history.append(float(result[1]))
		#fq_close_price:4
		stock_history.append(float(result[2]))
		#turn_over:12
		stock_history.append(float(result[3]))
		#total_value:13
		stock_history.append(float(result[4]))
		#circulation_value:14
		stock_history.append(float(result[5]))
		stock_history_list.append(stock_history)


		#future_price
		stock_price.append((result[6]))
		stock_price_list.append(stock_price)
	conn.commit()



	stock_history_arr = np.array(stock_history_list)

	sample_size=(len(stock_history_arr)+time_step-1)/time_step  #有size个sample


	#数据不一定需要有future_price
	mean = None
	std = None
	for i in range(len(stock_history_arr) - time_step):
		x = stock_history_arr[i:i+time_step,:6]
		
		mean = np.mean(x,axis=0)
		std = np.std(x,axis=0)

	test_x.append(x.tolist())

	#未来的真实值，可能为空
	future_price = stock_price_list[-1][0]




	return mean,std,test_x,future_price



	#标准化
	#mean=np.mean(stock_history_list,axis=0)
	#std=np.std(stock_history_list,axis=0)
	#normalized_test_data=(stock_history_list-mean)/std

	'''
	sample_size=(len(stock_history_arr)+time_step-1)/time_step  #有size个sample


	#数据不一定需要有future_price

	mean = None
	std = None
	for i in range(sample_size-1):
		x = stock_history_arr[i*time_step:(i+1)*time_step,:6]
		x = (x - np.mean(x,axis=0)) / np.std(x,axis=0)
		test_x.append(x.tolist())

	x = stock_history_arr[(i+1)*time_step:,:6]
	mean=np.mean(stock_history_arr[(i+1)*time_step:,:6],axis=0)
	std=np.std(stock_history_arr[(i+1)*time_step:,:6],axis=0)
	x = (x - np.mean(x,axis=0)) / np.std(x,axis=0)

	#标准差和方差均取与预测数据时间上最接近的一组即可
	
	test_x.append(x.tolist())

	#未来的真实值，可能为空
	future_price = stock_price_list[-1][0]




	return mean,std,test_x,future_price
	'''

def getCodeList(market):
	global conn
	global cursor
	stock_list = []
	cursor.execute(stock_sql.stock_market_select_sql , [market])
	results = cursor.fetchall()
	for result in results:
		stock_list.append(result[6])
	return stock_list


def predict_lstm(code,time_step,term,begin,end):
	with tf.variable_scope(code + '_' + term, reuse=None):
		#输入层、输出层权重、偏置
		weights={
				 'in':tf.Variable(tf.random_normal([input_size,rnn_unit])),
				 'out':tf.Variable(tf.random_normal([rnn_unit,1]))
				}
		biases={
				'in':tf.Variable(tf.constant(0.1,shape=[rnn_unit,])),
				'out':tf.Variable(tf.constant(0.1,shape=[1,]))
			   }

		X=tf.placeholder(tf.float32, shape=[None,time_step,input_size])
		batch_size=tf.shape(X)[0]
		time_step_tensor=tf.shape(X)[1]
		w_in=weights['in']
		b_in=biases['in']  
		input=tf.reshape(X,[-1,input_size])  #需要将tensor转成2维进行计算，计算后的结果作为隐藏层的输入
		input_rnn=tf.matmul(input,w_in)+b_in
		input_rnn=tf.reshape(input_rnn,[-1,time_step_tensor,rnn_unit])  #将tensor转成3维，作为lstm cell的输入
		cell=tf.nn.rnn_cell.BasicLSTMCell(rnn_unit)
		init_state=cell.zero_state(batch_size,dtype=tf.float32)
		output_rnn,final_states=tf.nn.dynamic_rnn(cell, input_rnn,initial_state=init_state, dtype=tf.float32)  #output_rnn是记录lstm每个输出节点的结果，final_states是最后一个cell的结果
		output=tf.reshape(output_rnn,[-1,rnn_unit]) #作为输出层的输入
		w_out=weights['out']
		b_out=biases['out']
		pred=tf.matmul(output,w_out)+b_out
		saver=tf.train.Saver()

		begindate=datetime.datetime.strptime(begin,'%Y-%m-%d')
		enddate=datetime.datetime.strptime(end,'%Y-%m-%d')

		while begindate<=enddate:
			date = begindate.strftime('%Y-%m-%d')

			mean,std,test_x,future_price = get_test_data(code,time_step,term,date)
			if len(test_x) == 0:
				begindate+=datetime.timedelta(days=1)
				continue


			with tf.Session() as sess:
				#参数恢复
				code_path = '/home/ayesha/data/models/'+code
				model_path = code_path + '/' + term
				module_file = tf.train.latest_checkpoint(model_path)
				saver.restore(sess, module_file)


				

				test_predict=[]
				for step in range(len(test_x)):
					prob=sess.run(pred,feed_dict={X:[test_x[step]]})
					predict=prob.reshape((-1))
					test_predict.extend(predict)
				#预测值
				test_predict=np.array(test_predict)*std[2]+mean[2]
				est_price = test_predict[-1]

				print('insert or update estimate data, code = '+code+', date = '+date +', term = ' + term)
				insert_or_update_data([code,date,
						est_price,
						future_price,
						est_price,
						future_price],term)
				
			begindate+=datetime.timedelta(days=1)


def insert_or_update_data(params,term):
	cursor.execute(''.join([
		'INSERT INTO stock_est_data ( ',
		'	`code`, ',
		'	date, ',
		'	est_price_'+term+', ',
		'	future_price_'+term+' '
		') ',
		'VALUES ',
		'	( ',
		'		% s ,% s ,% s ,% s ',
		'	) ON DUPLICATE KEY UPDATE est_price_' + term + ' = % s, ',
		'	future_price_' + term + ' = % s ',
		]),params)
	conn.commit()

def predict(time_step,term,begin,end):
	global conn
	global cursor
	conn = mdb.connect(host=config.mysql_ip, port=config.mysql_port,user=config.mysql_user,passwd=config.mysql_pass,db=config.mysql_db,charset='utf8')
	cursor = conn.cursor()

	for market in markets:
		code_list = getCodeList(market)
		for code in code_list:
			predict_lstm(code,time_step,term,begin,end)

	#关闭数据库连接
	cursor.close()
	conn.close()

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
	#predict_lstm(code,time_step,term,begin,end):
	predict_lstm('600000',30,'30','2013-01-01','2013-03-31')
	'''
	predict_lstm('600009',30,'30','2017-01-01','2017-03-01')
	predict_lstm('600010',30,'30','2017-01-01','2017-03-01')
	predict_lstm('600011',30,'30','2017-01-01','2017-03-01')
	predict_lstm('600012',30,'30','2017-01-01','2017-03-01')
	predict_lstm('600015',30,'30','2017-01-01','2017-03-01')
	predict_lstm('600016',30,'30','2017-01-01','2017-03-01')
	predict_lstm('600017',30,'30','2017-01-01','2017-03-01')
	'''
	db_close()