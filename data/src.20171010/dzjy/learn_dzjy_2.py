# -*- coding: UTF-8 -*-  
import numpy as np
import tensorflow as tf
import config
import MySQLdb as mdb
import os
import datetime
import decimal
import sys

#市场
markets = ['sh','sz']

#定义常量
rnn_unit=30
input_size=7
output_size=1
#学习率
lr=0.0006

conn = None
cursor = None


#获取训练集
def get_train_data(code,batch_size,time_step,term,begin,end):
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
            '                AND t.date >= %s  ',
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
        ]) , [end,begin,code])
    results = cursor.fetchall()
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

    conn.commit()

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
        #loss=abs(pred[-1][-1]-Y[-1][-1])


        loss=tf.reduce_mean(tf.square(tf.reshape(pred[time_step-1::time_step],[-1])-tf.reshape(Y[:,-1], [-1])))

        #learning_rate = tf.train.exponential_decay(LEARNING_RATE_BASE, 2001 * (len(batch_index)-1), len(batch_index)-1, LEARNING_RATE_DECAY)

        global_step = tf.Variable(0,name='global_step',trainable=False)
        train_op=tf.train.AdamOptimizer(lr).minimize(loss,global_step=global_step)
        saver=tf.train.Saver(max_to_keep=10)

        with tf.Session() as sess:
            sess.run(tf.global_variables_initializer())
            for i in range(config.TRAINING_STEPS + 1):
                for step in range(len(batch_index)-1):
                    final_states,loss_=sess.run([train_op,loss],feed_dict={X:train_x[batch_index[step]:batch_index[step+1]],Y:train_y[batch_index[step]:batch_index[step+1]]})
                    #print(train_y[batch_index[step]:batch_index[step+1]][-1][-1])
                    #print pred.eval()
                if i % 50==0:
                    print("save model : ", saver.save(sess, model_path + '/stock.model',global_step=global_step))

            print("save model : ", saver.save(sess, model_path + '/stock.model',global_step=global_step))

#训练函数
def train(batch_size,time_step,term,begin,end):
    for market in markets:
        code_list = getCodeList(market)
        for code in code_list:
            train_lstm(code,batch_size,time_step,term,begin,end)

def getCodeList(market):
    stock_list = []
    cursor.execute(''.join(['SELECT ',
                                'stock.stockType, ',
                                'stock.market, ',
                                'stock.`name`, ',
                                'stock.state, ',
                                'stock.currcapital, ',
                                'stock.profit_four, ',
                                'stock.`code`, ',
                                'stock.totalcapital, ',
                                'stock.mgjzc, ',
                                'stock.pinyin, ',
                                'stock.listing_date, ',
                                'stock.ct ',
                            'FROM ',
                                'stock ',
                            'WHERE ',
                                'stock.market = %s ']) , [market])
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

    code = sys.argv[1]
    batch_size = int(sys.argv[2])
    time_step = int(sys.argv[3])
    term = sys.argv[4]


    #train_lstm(code,batch_size,time_step,term,begin,end):
    train_lstm(code,batch_size , time_step , term , '2005-01-01' , '2016-12-31')
    #train( 80 , 30 , '30' , '2005-01-01' , '2016-12-31' )
    #train( 90 , 90 , '90' , '2005-01-01' , '2005-01-01' )
    #train( 180 , 180 , '180' , '2005-01-01' , '2005-01-01' )
    #train( 360 , 360 , '360' , '2005-01-01' , '2005-01-01' )
    db_close()
