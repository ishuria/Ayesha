# -*- coding: UTF-8 -*-  
import tensorflow as tf
import MySQLdb as mdb
from tensorflow.examples.tutorials.mnist import input_data
import config
import stock_sql

#入参维度
INPUT_NODE = 16
#出参维度
OUTPUT_NODE = 4


LAYER1_NODE = 500
BATCH_SIZE = 200


LEARNING_RATE_BASE = 0.8
LEARNING_RATE_DECAY = 0.99

REGULARIZATION_RATE = 0.0001
TRAINING_STEPS = 30000
MOVING_AVERAGE_DECAY = 0.99


#学习开始年份
LEARNING_YEAR_START = '2010'
#学习结束年份
LEARNING_YEAR_END = '2014'
#验证年份
VALIDATION_YEAR = '2015'
#市场
MARKETS = ['sh','sz']


def inference(input_tensor, avg_class, weights1, biases1, weights2, biases2):
	if avg_class == None:
		layer1 = tf.nn.softplus(tf.matmul(input_tensor, weights1) + biases1)
		return tf.matmul(layer1, weights2) + biases2
	else:
		layer1 = tf.nn.softplus(tf.matmul(input_tensor, avg_class.average(weights1)) + avg_class.average(biases1))
		return tf.matmul(layer1, avg_class.average(weights2)) + avg_class.average(biases2)

def train():
	x = tf.placeholder(tf.float32, [None, INPUT_NODE], name='x-input')
	y_ = tf.placeholder(tf.float32, [None, OUTPUT_NODE], name='y-input')

	weights1 = tf.Variable(tf.truncated_normal([INPUT_NODE, LAYER1_NODE], stddev=0.1))
	biases1 = tf.Variable(tf.constant(0.1, shape=[LAYER1_NODE]))

	weights2 = tf.Variable(tf.truncated_normal([LAYER1_NODE,OUTPUT_NODE], stddev=0.1))
	biases2 = tf.Variable(tf.constant(0.1, shape=[OUTPUT_NODE]))

	y = inference(x, None, weights1, biases1, weights2, biases2)

	global_step = tf.Variable(0,trainable=False)

	variable_averages = tf.train.ExponentialMovingAverage(MOVING_AVERAGE_DECAY, global_step)

	variable_averages_op = variable_averages.apply(tf.trainable_variables())

	average_y = inference(x, variable_averages, weights1, biases1, weights2, biases2)

	cross_entropy = tf.nn.sparse_softmax_cross_entropy_with_logits(logits=y, labels=tf.argmax(y_, 1))

	cross_entropy_mean = tf.reduce_mean(cross_entropy)

	regularizer = tf.contrib.layers.l2_regularizer(REGULARIZATION_RATE)

	regularization = regularizer(weights1) + regularizer(weights2)

	loss = cross_entropy_mean + regularization

	learning_rate = tf.train.exponential_decay(LEARNING_RATE_BASE, global_step, 200000 / BATCH_SIZE, LEARNING_RATE_DECAY)

	train_step = tf.train.GradientDescentOptimizer(learning_rate).minimize(loss, global_step=global_step)

	with tf.control_dependencies([train_step, variable_averages_op]):
		train_op = tf.no_op(name='train')

	#correct_prediction = tf.equal(tf.argmax(average_y, 1), tf.argmax(y_, 1))

	
	#误差在5%以内，认为成功
	abs_diff = tf.abs(tf.subtract(tf.Print(average_y,[average_y],summarize=100), tf.Print(y_,[y_],summarize=100), name=None))
	percent_diff = tf.div(abs_diff,y_)

	correct_prediction = tf.div(tf.add(tf.sign(tf.subtract(percent_diff,0.5)),1),2)


	'''
	tf.Print(average_y,[average_y])
	reduce_sum1 = tf.argmax(tf.Print(average_y,[average_y],summarize=100),1)
	reduce_sum2 = tf.argmax(tf.Print(y_,[y_]),1)
	'''
	

	#correct_prediction = tf.equal(reduce_sum1, reduce_sum2)

	accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

	with tf.Session() as sess:
		init = tf.global_variables_initializer()

		sess.run(init)

		conn = mdb.connect(host=config.mysql_ip, port=config.mysql_port,user=config.mysql_user,passwd=config.mysql_pass,db=config.mysql_db,charset='utf8')
		cursor = conn.cursor()

		#获取验证数据
		validation_data_list = []
		validation_result_list = []
		for market in MARKETS:
				code_list = getCodeList(market)
				for code in code_list:
					print(code + ',validating...')
					read_train_data(VALIDATION_YEAR,code,cursor,validation_data_list,validation_result_list)
					if len(validation_data_list) >= 10000 or len(validation_result_list) >= 10000:
						break


		#print(validation_result_list)
		validate_feed = {x:validation_data_list,y_:validation_result_list}

		#test_feed = {x:mnist.test.images, y_:mnist.test.labels}

		current_year = LEARNING_YEAR_START
		#每年
		while current_year <= LEARNING_YEAR_END:
			
			#每个市场
			for market in MARKETS:
				code_list = getCodeList(market)
				for code in code_list:
					train_data_list = []
					train_result_list = []
					

					read_train_data(current_year,code,cursor,train_data_list,train_result_list)
					if len(train_data_list) == 0 or len(train_result_list) == 0:
						continue
					print(code + '  ' + current_year)

					#print(train_data_list)

					#print(train_result_list)

					sess.run(train_op, feed_dict={x:train_data_list,y_:train_result_list})
			validate_acc = sess.run(accuracy, feed_dict=validate_feed)
			print('After ' + current_year + ' training, validation accuracy using average model is %g' % (validate_acc))
			current_year = str(int(current_year) + 1)

		'''
		for i in range(TRAINING_STEPS):
			if i % 1000 == 0:
				#使用验证数据测试准确率
				validate_acc = sess.run(accuracy, feed_dict=validate_feed)
				print("After %d training step(s), validation accuracy using average model is %g" % (i, validate_acc))

			#获取下一批训练数据
			xs, ys = mnist.train.next_batch(BATCH_SIZE)

			sess.run(train_op, feed_dict={x:xs,y_:ys})
		'''

		conn.commit()
		cursor.close()
		conn.close()

		#test_acc = sess.run(accuracy, feed_dict=test_feed)
		#print("After %d training step(s), test accuracy using average model is %g" % (TRAINING_STEPS, test_acc))

def main(argv=None):
	#mnist = input_data.read_data_sets("/home/ayesha/mnist", one_hot=True)
	#print(mnist.validation)
	train()

#获取每一年的数据，返回一个矩阵
def read_train_data(year,code,cursor,train_data_list,train_result_list):
	year_start = year + '-01-01'
	year_end = year + '-12-31'
	cursor.execute(''.join([
							'SELECT ',
								't.inc_30 , ',
								't.inc_90 , ',
								't.inc_180 , ',
								't.inc_360 , ',
								't.turn_30 , ',
								't.turn_90 , '
								't.turn_180 , ',
								't.turn_360 , ',
								't.trade_money_30 , ',
								't.trade_money_90 , ',
								't.trade_money_180 , ',
								't.trade_money_360 , ',
								't.trade_num_30 , ',
								't.trade_num_90 , ',
								't.trade_num_180 , ',
								't.trade_num_360 , ',
								't.future_inc_30 , ',
								't.future_inc_90 , ',
								't.future_inc_180 , ',
								't.future_inc_360  ',
							'FROM ',
								'stock_train_data t ',
							'WHERE ',
								't.date >= %s ',
							'AND t.date <= %s ',
							'AND t.`code` = %s ',
							]), [year_start,year_end,code])

	results = cursor.fetchall()
	for result in results:
		train_data = []
		if result[0] == None:
			continue
		train_data.append(result[0])

		if result[1] == None:
			continue
		train_data.append(result[1])

		if result[2] == None:
			continue
		train_data.append(result[2])

		if result[3] == None:
			continue
		train_data.append(result[3])

		if result[4] == None:
			continue
		train_data.append(result[4])

		if result[5] == None:
			continue
		train_data.append(result[5])

		if result[6] == None:
			continue
		train_data.append(result[6])

		if result[7] == None:
			continue
		train_data.append(result[7])

		if result[8] == None:
			continue
		train_data.append(result[8])

		if result[9] == None:
			continue
		train_data.append(result[9])

		if result[10] == None:
			continue
		train_data.append(result[10])

		if result[11] == None:
			continue
		train_data.append(result[11])

		if result[12] == None:
			continue
		train_data.append(result[12])

		if result[13] == None:
			continue
		train_data.append(result[13])

		if result[14] == None:
			continue
		train_data.append(result[14])

		if result[15] == None:
			continue
		train_data.append(result[15])
		






		train_result = []
		if result[16] == None:
			continue
		train_result.append(result[16])

		if result[17] == None:
			continue
		train_result.append(result[17])

		if result[18] == None:
			continue
		train_result.append(result[18])
		
		if result[19] == None:
			continue
		train_result.append(result[19])

		train_result_list.append(train_result)
		train_data_list.append(train_data)

	return train_data_list

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
	tf.app.run()