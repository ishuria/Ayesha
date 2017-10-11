# -*- coding: UTF-8 -*-  
import numpy as np
import tensorflow as tf
import datetime
import decimal
import sys
import db.db as db
import db.stock as stock
import db.stock_est_data as stock_est_data
import config

input_size=7

rnn_unit=30


#获取测试集
def get_test_data(code,time_step,term,date,cursor):
    mean,std,test_x,future_price = None,None,[],None

    stock_history_list = []
    stock_price_list = []
    
    results = stock.get_estimation_data(code,date,config.MAX_DATA_SIZE,cursor)

    for result in results:
        stock_history = []
        stock_price = []

        if result[0] is None:
            continue
        stock_history.append((result[0]))

        if result[1] is None:
            continue
        stock_history.append((result[1]))

        if result[2] is None:
            continue
        stock_history.append((result[2]))

        if result[3] is None:
            continue
        stock_history.append((result[3]))

        if result[4] is None:
            continue
        stock_history.append((result[4]))

        if result[5] is None:
            continue
        stock_history.append((result[5]))

        if result[6] is None:
            continue
        stock_history.append((result[6]))

        stock_history_list.append(stock_history)

        #future_price
        stock_price.append((result[7]))
        stock_price_list.append(stock_price)

    if len(stock_history_list) == 0:
        return mean,std,test_x,future_price

    stock_history_arr = np.array(stock_history_list)


    trade_num_arr = stock_history_arr[:,0]
    trade_num_arr = (trade_num_arr - np.mean(trade_num_arr,axis=0)) / np.std(trade_num_arr,axis=0)


    fq_close_price_arr = stock_history_arr[:,1]
    mean = np.mean(fq_close_price_arr,axis=0)
    std = np.std(fq_close_price_arr,axis=0)
    fq_close_price_arr = (fq_close_price_arr - np.mean(fq_close_price_arr,axis=0)) / np.std(fq_close_price_arr,axis=0)

    trade_money = stock_history_arr[:,2]
    trade_money = (trade_money - np.mean(trade_money,axis=0)) / np.std(trade_money,axis=0)

    circulation_value = stock_history_arr[:,3]
    circulation_value = (circulation_value - np.mean(circulation_value,axis=0)) / np.std(circulation_value,axis=0)


    stock_history_arr[:,0] = trade_num_arr
    stock_history_arr[:,1] = fq_close_price_arr
    stock_history_arr[:,2] = trade_money
    stock_history_arr[:,3] = circulation_value

    #标准差和方差均取与预测数据时间上最接近的一组即可
    test_x.append(stock_history_arr[-1*time_step:].tolist())

    #未来的真实值，可能为空
    future_price = stock_price_list[-1][0]

    return mean,std,test_x,future_price

def predict_lstm(code,time_step,term,date,cursor):
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

        mean,std,test_x,future_price = get_test_data(code,time_step,term,date,cursor)

        if len(test_x) == 0:
            return

        with tf.Session() as sess:
            #参数恢复
            code_path = '/home/ayesha/data/models/'+code
            model_path = code_path + '/' + term
            module_file = tf.train.latest_checkpoint(model_path)
            saver.restore(sess, module_file)

            test_predict=[]
            for step in range(len(test_x)):
                prob = sess.run(pred,feed_dict={X:[test_x[step]]})
                predict = prob.reshape((-1))
                test_predict.extend(predict)

            #预测值
            test_predict = np.array(test_predict) * float(std) + float(mean)
            #print(test_predict)
            est_price = test_predict[-1]

            print('refreshing stock est data ' + code + ' ' + date)
            params = [code,date,
                    est_price,
                    future_price,
                    est_price,
                    future_price]
            stock_est_data.refresh_stock_est_data(params,cursor)


if __name__ == '__main__':
    conn,cursor = db.db_connect()
    code = sys.argv[1]
    time_step = int(sys.argv[2])
    term = sys.argv[3]
    date = sys.argv[4]
    predict_lstm(code,time_step,term,date,cursor)
    conn.commit()
    db.db_close(conn,cursor)