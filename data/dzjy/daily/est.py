# -*- coding: UTF-8 -*-  
import numpy as np
import tensorflow as tf
import config
import MySQLdb as mdb
import datetime
import decimal
import sys

conn = None
cursor = None

input_size=7

rnn_unit=30


#获取测试集
def get_test_data(code,time_step,term,date):
    mean,std,test_x,future_price = None,None,[],None

    stock_history_list = []
    stock_price_list = []
    cursor.execute(''.join([
            '       SELECT ',
            '            * ',
            '        FROM ',
            '            ( ',
            '                SELECT ',
            '                    t.trade_num, ',
            '                    t.fq_close_price, ',
            '                    t.trade_money,  ',
            '                    t.circulation_value,  ',
            '                    t.trade_money / t.circulation_value * 100 trade_rate, ',
            '                    t.turnover_rate, ',
            '                    ifnull( ',
            '                        sum(t2.tvol * t2.PRICE * 10000) / t.circulation_value * 100, ',
            '                        0 ',
            '                    ) dzjy_rate, ',
            '                    d.future_price_30, ',
            '                    t.date ',
            '                FROM ',
            '                    stock_history t ',
            '                LEFT JOIN dzjy_history t2 ON t.date = t2.tdate ',
            '                AND t.`code` = t2.secucode ',
            '                LEFT JOIN stock_train_data d ON d.`code` = t.`code` ',
            '                AND d.date = t.date ',
            '                WHERE ',
            '                    t.date <= %s  ',
            '                AND t.`code` = %s  ',
            '                AND t.date IS NOT NULL ',
            '                AND t.trade_num IS NOT NULL ',
            '                AND t.trade_money IS NOT NULL ',
            '                AND t.fq_close_price IS NOT NULL ',
            '                AND t.turnover_rate IS NOT NULL ',
            '                AND d.future_price_30 IS NOT NULL ',
            '                AND t.close_price IS NOT NULL ',
            '                GROUP BY ',
            '                    t.date, ',
            '                    t.close_price, ',
            '                    t.trade_num, ',
            '                    t.trade_money, ',
            '                    t.fq_close_price, ',
            '                    t.turnover_rate, ',
            '                    d.future_price_30 ',
            '                ORDER BY ',
            '                    t.date DESC ',
            '                LIMIT 0, ',
            '                '+ str(config.MAX_DATA_SIZE) +' ',
            '            ) tt ',
            '        ORDER BY ',
            '            date ASC',
        ]) , [date,code])
    results = cursor.fetchall()
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
    conn.commit()




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

def predict_lstm(code,time_step,term,date):
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

        mean,std,test_x,future_price = get_test_data(code,time_step,term,date)

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

            print('insert or update estimate data, code = '+code+', date = '+date +', term = ' + term)
            insert_or_update_data([code,date,
                    est_price,
                    future_price,
                    est_price,
                    future_price],term)


def insert_or_update_data(params,term):
    cursor.execute(''.join([
        'INSERT INTO stock_est_data ( ',
        '   `code`, ',
        '   date, ',
        '   est_price_'+term+', ',
        '   future_price_'+term+' '
        ') ',
        'VALUES ',
        '   ( ',
        '       % s ,% s ,% s ,% s ',
        '   ) ON DUPLICATE KEY UPDATE est_price_' + term + ' = % s, ',
        '   future_price_' + term + ' = % s ',
        ]),params)
    conn.commit()

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
    code = sys.argv[1]
    time_step = int(sys.argv[2])
    term = sys.argv[3]
    date = sys.argv[4]
    predict_lstm(code,time_step,term,date)
    db_close()