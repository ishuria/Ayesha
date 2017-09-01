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
rnn_unit=10

#获取测试集
def get_test_data(code,time_step=20,date='2017-01-01'):
	global conn
	global cursor

	mean,std,test_x,future_price_30,future_price_90,future_price_180,future_price_360 = None,None,[],None,None,None,None
	#如果当天不是交易日，返回空
	cursor.execute('SELECT count(1) count FROM stock_history WHERE stock_history.`code` = %s AND stock_history.date = %s', [code, date])
	result = cursor.fetchone()
	count = result[0]
	#如果有记录，更新
	if count == 0:
		return mean,std,test_x,future_price_30,future_price_90,future_price_180,future_price_360

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
			'			a.future_price_30, ',
			'			a.future_price_90, ',
			'			a.future_price_180, ',
			'			a.future_price_360, ',
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
			'		360 ',
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
		#close_price:4
		stock_history.append(float(result[2]))
		#turn_over:12
		stock_history.append(float(result[3]))
		#total_value:13
		stock_history.append(float(result[4]))
		#circulation_value:14
		stock_history.append(float(result[5]))
		#future_price_30
		stock_history.append(float(result[6]))
		#future_price_90
		stock_history.append(float(result[7]))
		#future_price_180
		stock_history.append(float(result[8]))
		#future_price_360
		stock_history.append(float(result[9]))
		stock_history_list.append(stock_history)
	conn.commit()

	#标准化
	mean=np.mean(stock_history_list,axis=0)
	std=np.std(stock_history_list,axis=0)
	normalized_test_data=(stock_history_list-mean)/std

	size=(len(normalized_test_data)+time_step-1)/time_step  #有size个sample


	#数据不一定需要有future_price
	for i in range(size-1):
	   x=normalized_test_data[i*time_step:(i+1)*time_step,:6]
	   test_x.append(x.tolist())
	test_x.append((normalized_test_data[(i+1)*time_step:,:6]).tolist())
	future_price_30 = stock_history_list[-1][6]
	future_price_90 = stock_history_list[-1][7]
	future_price_180 = stock_history_list[-1][8]
	future_price_360 = stock_history_list[-1][9]
	return mean,std,test_x,future_price_30,future_price_90,future_price_180,future_price_360

def getCodeList(market):
	global conn
	global cursor
	stock_list = []
	cursor.execute(stock_sql.stock_market_select_sql , [market])
	results = cursor.fetchall()
	for result in results:
		stock_list.append(result[6])
	return stock_list

#——————————————————定义神经网络变量——————————————————
#输入层、输出层权重、偏置
weights={
		 'in':tf.Variable(tf.random_normal([input_size,rnn_unit])),
		 'out':tf.Variable(tf.random_normal([rnn_unit,1]))
		}
biases={
		'in':tf.Variable(tf.constant(0.1,shape=[rnn_unit,])),
		'out':tf.Variable(tf.constant(0.1,shape=[1,]))
	   }

#——————————————————定义神经网络变量——————————————————
def lstm(X):	 
	batch_size=tf.shape(X)[0]
	time_step=tf.shape(X)[1]
	w_in=weights['in']
	b_in=biases['in']  
	input=tf.reshape(X,[-1,input_size])  #需要将tensor转成2维进行计算，计算后的结果作为隐藏层的输入
	input_rnn=tf.matmul(input,w_in)+b_in
	input_rnn=tf.reshape(input_rnn,[-1,time_step,rnn_unit])  #将tensor转成3维，作为lstm cell的输入
	cell=tf.nn.rnn_cell.BasicLSTMCell(rnn_unit)
	init_state=cell.zero_state(batch_size,dtype=tf.float32)
	output_rnn,final_states=tf.nn.dynamic_rnn(cell, input_rnn,initial_state=init_state, dtype=tf.float32)
	output=tf.reshape(output_rnn,[-1,rnn_unit]) #作为输出层的输入
	w_out=weights['out']
	b_out=biases['out']
	pred=tf.matmul(output,w_out)+b_out
	return pred,final_states

#————————————————预测模型————————————————————
def predict_lstm(code,time_step=20,begin='2010-01-01',end='2014-12-31'):
	global conn
	global cursor

	conn = mdb.connect(host=config.mysql_ip, port=config.mysql_port,user=config.mysql_user,passwd=config.mysql_pass,db=config.mysql_db,charset='utf8')
	cursor = conn.cursor()

	begindate=datetime.datetime.strptime(begin,'%Y-%m-%d')
	enddate=datetime.datetime.strptime(end,'%Y-%m-%d')

	while begindate<=enddate:
		date = begindate.strftime('%Y-%m-%d')
		mean,std,test_x,future_price_30,future_price_90,future_price_180,future_price_360 = get_test_data(code,time_step,date)

		#如果当天不是交易日，继续下一天
		if len(test_x) == 0:
			begindate+=datetime.timedelta(days=1)
			continue

		est_price_30 = predict_lstm_sub(code,time_step,mean,std,test_x,'30')
		est_price_90 = predict_lstm_sub(code,time_step,mean,std,test_x,'90')
		est_price_180 = predict_lstm_sub(code,time_step,mean,std,test_x,'180')
		est_price_360 = predict_lstm_sub(code,time_step,mean,std,test_x,'360')
		
		cursor.execute('SELECT count(1) count from stock_est_data where stock_est_data.`code` = %s and stock_est_data.date = %s' , [code, date])
		result = cursor.fetchone()
		count = result[0]
		#如果有记录，更新
		if count == 1:
			print('update estimate code = ' + code + ',date = ' + date)
			insert_stock_est_data([
				est_price_30,
				est_price_90,
				est_price_180,
				est_price_360,
				future_price_30,
				future_price_90,
				future_price_180,
				future_price_360,
				code,date])
		#否则新增数据
		else:
			print('insert estimate code = ' + code + ',date = ' + date)
			update_stock_est_data([
						code,date,
						est_price_30,
						est_price_90,
						est_price_180,
						est_price_360,
						future_price_30,
						future_price_90,
						future_price_180,
						future_price_360])

		'''
		test_y=np.array(test_y)*std[2]+mean[2]
		test_predict=np.array(test_predict)*float(std[2])+float(mean[2])
		acc=np.average(np.abs(test_predict-test_y[:len(test_predict)])/test_y[:len(test_predict)])
		np.savetxt("test_y.txt", test_y);
		np.savetxt("test_predict.txt", test_predict);
		print(acc)
		'''
		conn.commit()
		begindate+=datetime.timedelta(days=1)
	
	#关闭数据库连接
	cursor.close()
	conn.close()


def predict_lstm_sub(code,time_step,mean,std,test_x,term):
	with tf.variable_scope(code + '_' + term, reuse=None):
		with tf.Session() as sess:
			X=tf.placeholder(tf.float32, shape=[None,time_step,input_size])
			#Y=tf.placeholder(tf.float32, shape=[None,time_step,output_size])
			pred,_=lstm(X)
			saver=tf.train.Saver(tf.global_variables())
		
			#参数恢复
			code_path = '/home/ayesha/data/models/'+code
            model_path = code_path + '/' + term

			module_file = tf.train.latest_checkpoint(model_path)
			#30天
			saver.restore(sess, module_file)
			test_predict=[]
			for step in range(len(test_x)-1):
				prob=sess.run(pred,feed_dict={X:[test_x[step]]})
				predict=prob.reshape((-1))
				test_predict.extend(predict)
			#预测值
			test_predict=np.array(test_predict)*std+mean
			est_price = test_predict[-1]
			return est_price

def insert_stock_est_data(params):
	global cursor
	cursor.execute(''.join([
						'UPDATE stock_est_data t ',
						'SET t.est_price_30 = % s, ',
						' t.est_price_90 = % s, ',
						' t.est_price_180 = % s, ',
						' t.est_price_360 = % s, ',
						' t.future_price_30 = % s, ',
						' t.future_price_90 = % s, ',
						' t.future_price_180 = % s, ',
						' t.future_price_360 = % s ',
						'WHERE ',
						'	t.`code` = % s ',
						'AND t.date = % s '
						]),params)

def update_stock_est_data(params):
	global cursor
	cursor.execute(''.join(['INSERT INTO stock_est_data ( ',
								'stock_est_data.`code`, ',
								'stock_est_data.date, ',
								'stock_est_data.est_price_30, ',
								'stock_est_data.est_price_90, ',
								'stock_est_data.est_price_180, ',
								'stock_est_data.est_price_360, ',
								'stock_est_data.future_price_30, ',
								'stock_est_data.future_price_90, ',
								'stock_est_data.future_price_180, ',
								'stock_est_data.future_price_360 ',
							') ',
							'VALUES ',
								'( ',
									'%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s,%s ',
								') ']),params)

def predict(time_step,begin,end):
	global conn
	global cursor
	conn = mdb.connect(host=config.mysql_ip, port=config.mysql_port,user=config.mysql_user,passwd=config.mysql_pass,db=config.mysql_db,charset='utf8')
	cursor = conn.cursor()

	for market in markets:
		code_list = getCodeList(market)
		for code in code_list:
			predict_lstm(code,time_step,begin,end)

	#关闭数据库连接
	cursor.close()
	conn.close()




if __name__ == '__main__':
	#predict(15,'2005-01-01','2014-12-31')
	predict_lstm('600000',15,'2015-01-01','2015-12-31')