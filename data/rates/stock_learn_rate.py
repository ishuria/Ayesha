# -*- coding: UTF-8 -*-  
import numpy as np
import tensorflow as tf
import config
import MySQLdb as mdb
import os
import datetime
import decimal

#市场
markets = ['sh','sz']

#定义常量
rnn_unit=30
input_size=5
output_size=1
#学习率
lr=0.0006

conn = None
cursor = None

LEARNING_RATE_BASE = 0.8
LEARNING_RATE_DECAY = 0.99

TRAINING_STEPS = 2000

#获取训练集
def get_train_data(code,batch_size,time_step,term,begin,end):
    stock_history_list = []
    stock_price_list = []
    cursor.execute(''.join([
            'SELECT ',
            '    t.trade_num_rate, ',
            '    t.trade_money_rate, ',
            '    t.total_value_rate, ',
            '    t.circulation_value_rate, ',
            '    t.fq_close_price_rate, ',
            '    t.next_fq_close_price_rate ',
            'FROM ',
            '    stock_rate t ',
            'WHERE ',
            '    t.`code` = %s',
            '    AND t.date <= %s ',
            '    AND t.date >= %s ',
            'ORDER BY ',
            '    t.date ASC '
        ]) , [code,end,begin])
    results = cursor.fetchall()
    for result in results:
        stock_history = []
        stock_price = []
        #trade_num:2
        if result[0] is None:
            continue
        stock_history.append(result[0])
        #trade_money:3
        if result[1] is None:
            continue
        stock_history.append(result[1])
        #close_price:4
        if result[2] is None:
            continue
        stock_history.append(result[2])
        #turn_over:12
        if result[3] is None:
            continue
        stock_history.append(result[3])
        #total_value:13
        if result[4] is None:
            continue
        stock_history.append(result[4])

        if result[5] is None:
            continue
        stock_price.append(result[5])
        
        stock_history_list.append(stock_history)
        stock_price_list.append(stock_price)

    conn.commit()

    stock_history_arr = np.array(stock_history_list)
    stock_price_arr = np.array(stock_price_list)

    #训练集输入
    train_x = []
    #训练集输出
    train_y = []

    batch_index=[]
    for i in range(len(stock_history_arr) - time_step):
       if i % batch_size==0:
           batch_index.append(i)
       x = stock_history_arr[i:i+time_step,:5]
       #x = stock_history_list[i:i+time_step]
       #标准化，在每一个time_step组内进行标准化
       #x = (x - np.mean(x,axis=0)) / np.std(x,axis=0)
       #print(x)
       y = stock_price_arr[i:i+time_step,0,np.newaxis]
       #y = stock_price_list[i:i+time_step,np.newaxis]
       #y = (y - np.mean(y,axis=0)) / np.std(y,axis=0)
       
       #print(y)
       train_x.append(x.tolist())
       train_y.append(y.tolist())

    batch_index.append((len(stock_history_arr)-time_step))
    return batch_index,train_x,train_y



def train_lstm(code,batch_size,time_step,term,begin,end):
    with tf.variable_scope(code + '_' + term, reuse=None):
        code_path = '/home/ayesha/data/models/'+code
        model_path = code_path + '/' + term
        if not os.path.exists(code_path):
            os.mkdir(code_path)

        if not os.path.exists(model_path):
            os.mkdir(model_path)

        X=tf.placeholder(tf.float32, shape=[None,time_step,input_size])
        Y=tf.placeholder(tf.float32, shape=[None,time_step,output_size])
        batch_index,train_x,train_y = get_train_data(code,batch_size,time_step,term,begin,end)
        weights={
             'in':tf.Variable(tf.random_normal([input_size,rnn_unit])),
             'out':tf.Variable(tf.random_normal([rnn_unit,1]))
            }
        biases={
                'in':tf.Variable(tf.constant(0.1,shape=[rnn_unit,])),
                'out':tf.Variable(tf.constant(0.1,shape=[1,]))
               }
        batch_size_variable=tf.shape(X)[0]
        time_step_variable=tf.shape(X)[1]
        w_in=weights['in']
        b_in=biases['in']  
        input=tf.reshape(X,[-1,input_size])  #需要将tensor转成2维进行计算，计算后的结果作为隐藏层的输入
        input_rnn=tf.matmul(input,w_in)+b_in
        input_rnn=tf.reshape(input_rnn,[-1,time_step_variable,rnn_unit])  #将tensor转成3维，作为lstm cell的输入
        cell=tf.nn.rnn_cell.BasicLSTMCell(rnn_unit)
        init_state=cell.zero_state(batch_size_variable,dtype=tf.float32)
        output_rnn,final_states=tf.nn.dynamic_rnn(cell, input_rnn,initial_state=init_state, dtype=tf.float32)
        output=tf.reshape(output_rnn,[-1,rnn_unit]) #作为输出层的输入
        w_out=weights['out']
        b_out=biases['out']
        pred=tf.matmul(output,w_out)+b_out

        #损失函数
        loss=tf.reduce_mean(tf.square(tf.reshape(pred,[-1])-tf.reshape(Y, [-1])))

        #learning_rate = tf.train.exponential_decay(LEARNING_RATE_BASE, 2001 * (len(batch_index)-1), len(batch_index)-1, LEARNING_RATE_DECAY)

        global_step = tf.Variable(0,name='global_step',trainable=False)
        train_op=tf.train.AdamOptimizer(lr).minimize(loss,global_step=global_step)
        saver=tf.train.Saver(tf.global_variables(),max_to_keep=0)

        with tf.Session() as sess:
            sess.run(tf.global_variables_initializer())
            for i in range(TRAINING_STEPS + 1):
                for step in range(len(batch_index)-1):
                    final_states,loss_=sess.run([train_op,loss],feed_dict={X:train_x[batch_index[step]:batch_index[step+1]],Y:train_y[batch_index[step]:batch_index[step+1]]})
                if i % 10==0:
                    print("save model : ", saver.save(sess, model_path + '/stock.model',global_step=global_step))

#训练函数
def train(batch_size,time_step,term,begin,end):
    for market in markets:
        code_list = getCodeList(market)
        for code in code_list:
            train_lstm(code,batch_size,time_step,term,begin,end)

def getCodeList(market):
    stock_list = []
    cursor.execute(stock_sql.stock_market_select_sql , [market])
    results = cursor.fetchall()
    for result in results:
        stock_list.append(result[6])
    return stock_list

def db_connect():
    global conn
    global cursor
    conn = mdb.connect(host=config.mysql_ip, port=config.mysql_port,user=config.mysql_user,passwd=config.mysql_pass,db=config.mysql_db,charset='utf8')
    cursor = conn.cursor()

def db_close():
    #关闭数据库连接
    cursor.close()
    conn.close()

if __name__ == '__main__':
    db_connect()
    #train_lstm(code,batch_size,time_step,term,begin,end):
    train_lstm('600000',80 , 30 , '30' , '2005-01-01' , '2012-12-31')
    #train( 30 , 30 , '30' , '2005-01-01' , '2016-12-31' )
    #train( 90 , 90 , '90' , '2005-01-01' , '2005-01-01' )
    #train( 180 , 180 , '180' , '2005-01-01' , '2005-01-01' )
    #train( 360 , 360 , '360' , '2005-01-01' , '2005-01-01' )
    db_close()
