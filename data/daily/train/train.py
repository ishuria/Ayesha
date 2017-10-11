# -*- coding: UTF-8 -*-  
import numpy as np
import tensorflow as tf
import config
import MySQLdb as mdb
import os
import sys
import db.db as db
import db.stock as stock

#定义常量
rnn_unit=30
input_size=7
output_size=1

#学习率
lr=0.0006

#获取训练集
def get_train_data(code,batch_size,time_step,term,date,cursor):
    stock_history_list = []
    stock_price_list = []
    results = stock.get_train_data(code,date,config.MAX_DATA_SIZE,cursor)
    for result in results:
        stock_history = []
        stock_price = []

        if result[0] is None:
            continue
        stock_history.append(result[0])

        if result[1] is None:
            continue
        stock_history.append(result[1])

        if result[2] is None:
            continue
        stock_history.append(result[2])

        if result[3] is None:
            continue
        stock_history.append(result[3])

        if result[4] is None:
            continue
        stock_history.append(result[4])

        if result[5] is None:
            continue
        stock_history.append(result[5])

        if result[6] is None:
            continue
        stock_history.append(result[6])

        if result[7] is None:
            continue
        stock_price.append(result[7])
        
        stock_history_list.append(stock_history)
        stock_price_list.append(stock_price)

    stock_history_arr = np.array(stock_history_list)
    stock_price_arr = np.array(stock_price_list)

    #全局标准化
    if len(stock_history_arr) == 0:
        return [],[],[]

    trade_num_arr = stock_history_arr[:,0]
    trade_num_arr = (trade_num_arr - np.mean(trade_num_arr,axis=0)) / np.std(trade_num_arr,axis=0)

    fq_close_price_arr = stock_history_arr[:,1]
    mean = np.mean(fq_close_price_arr,axis=0)
    std = np.std(fq_close_price_arr,axis=0)
    fq_close_price_arr = (fq_close_price_arr - mean) / std

    trade_money = stock_history_arr[:,2]
    trade_money = (trade_money - np.mean(trade_money,axis=0)) / np.std(trade_money,axis=0)

    circulation_value = stock_history_arr[:,3]
    circulation_value = (circulation_value - np.mean(circulation_value,axis=0)) / np.std(circulation_value,axis=0)

    stock_history_arr[:,0] = trade_num_arr
    stock_history_arr[:,1] = fq_close_price_arr
    stock_history_arr[:,2] = trade_money
    stock_history_arr[:,3] = circulation_value
    stock_price_arr = (stock_price_arr - np.mean(stock_price_arr,axis=0)) / np.std(stock_price_arr,axis=0)

    #训练集输入
    train_x = []
    #训练集输出
    train_y = []

    batch_index=[]
    for i in range(len(stock_history_arr) - time_step):
        if i % batch_size==0:
           batch_index.append(i)
        x = stock_history_arr[i:i+time_step,:8]
        y = stock_price_arr[i:i+time_step,0,np.newaxis]
        train_x.append(x.tolist())
        train_y.append(y.tolist())

    batch_index.append((len(stock_history_arr)-time_step))
    return batch_index,train_x,train_y

def daily_train_lstm(code,batch_size,time_step,term,date,cursor):
    with tf.variable_scope(code + '_' + term, reuse=None):
        code_path = '/home/ayesha/data/models/'+code
        model_path = code_path + '/' + term
        if not os.path.exists(code_path):
            os.mkdir(code_path)

        if not os.path.exists(model_path):
            os.mkdir(model_path)

        X=tf.placeholder(tf.float32, shape=[None,time_step,input_size])
        Y=tf.placeholder(tf.float32, shape=[None,time_step,output_size])
        batch_index,train_x,train_y = get_train_data(code,batch_size,time_step,term,date,cursor)
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
        pred = tf.matmul(output,w_out) + b_out

        loss=tf.reduce_mean(tf.square(tf.reshape(pred[time_step-1::time_step],[-1])-tf.reshape(Y[:,-1], [-1])))

        global_step = tf.Variable(0,name='global_step',trainable=False)
        train_op=tf.train.AdamOptimizer(lr).minimize(loss,global_step=global_step)
        saver=tf.train.Saver(max_to_keep=10)

        with tf.Session() as sess:
        	#参数恢复
            code_path = '/home/ayesha/data/models/'+code
            model_path = code_path + '/' + term
            module_file = tf.train.latest_checkpoint(model_path)
            saver.restore(sess, module_file)
            #训练
            for i in range(config.DAILY_TRAINING_STEPS + 1):
                for step in range(len(batch_index)-1):
                    final_states,loss_=sess.run([train_op,loss],feed_dict={X:train_x[batch_index[step]:batch_index[step+1]],Y:train_y[batch_index[step]:batch_index[step+1]]})
            #保存模型
            print("save model : ", saver.save(sess, model_path + '/stock.model',global_step=global_step))

if __name__ == '__main__':
    conn,cursor = db.db_connect()
    code = sys.argv[1]
    batch_size = int(sys.argv[2])
    time_step = int(sys.argv[3])
    term = sys.argv[4]
    date = sys.argv[5]
    daily_train_lstm(code, batch_size, time_step, term, date,cursor)
    db.db_close(conn,cursor)