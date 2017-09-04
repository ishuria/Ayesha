# -*- coding: UTF-8 -*-  
import numpy as np
import tensorflow as tf
import config
import MySQLdb as mdb
import stock_sql
import os
import datetime
import gc


import psutil

#市场
markets = ['sh','sz']


#定义常量
rnn_unit=30
input_size=6
output_size=1
#学习率
lr=0.0006


conn = None
cursor = None

train_x = []
train_y = []

#一次性取出所有数据
def get_all_train_data(code,term,begin,end):
    enddate = datetime.datetime(int(end[0:4]),int(end[5:7]),int(end[8:10]))
    begindate = datetime.datetime(int(begin[0:4]),int(begin[5:7]),int(begin[8:10]))
    diff = (enddate-begindate).days

    stock_history_list = []
    stock_price_list = []
    cursor.execute(''.join([
            'SELECT ',
            '    * ',
            'FROM ',
            '    ( ',
            '        SELECT ',
            '            t.trade_num, ',
            '            t.trade_money, ',
            '            t.fq_close_price, ',
            '            t.turnover_rate, ',
            '            t.total_value, ',
            '            t.circulation_value, ',
            '            a.future_price_'+term+', ',
            '            t.date ',
            '        FROM ',
            '            stock_history t ',
            '        INNER JOIN stock_train_data a ON a.`code` = t.`code` ',
            '        AND a.date = t.date ',
            '        WHERE ',
            '            t.date <= %s ',
            '        AND t.`code` = %s ',
            '        ORDER BY ',
            '            t.date DESC ',
            '        LIMIT 0, ',
            '        '+ str(config.lstm_data_size+diff) + ' ',
            '    ) tt ',
            'ORDER BY ',
            '    tt.date ASC '
        ]) , [end,code])
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
        #circulation_value:14
        if result[5] is None:
            continue
        stock_history.append(result[5])
        
        if result[6] is None:
            continue
        stock_price.append(result[6])


        if result[7] is None:
            continue
        stock_history.append(result[7])
        stock_price.append(result[7])
        stock_history_list.append(stock_history)
        stock_price_list.append(stock_price)
    conn.commit()
    return stock_history_list,stock_price_list

#从内存中取出训练要用的数据
def get_train_data(stock_history_list,stock_price_list,batch_size,time_step,term,date):
    global train_x
    global train_y
    #获取当前运行的pid  
    p1=psutil.Process(os.getpid())
    sub_history_list = []
    sub_price_list = []

    print "percent : %.2f%%" % (p1.memory_percent())

    start_collect = False
    data_count = 0
    for i in range(len(stock_history_list)-1,-1,-1):
        price_date = stock_history_list[i][6]
        if date == price_date:
            start_collect = True
        if start_collect:
            sub_history = []
            sub_history.append(stock_history_list[i][0])
            sub_history.append(stock_history_list[i][1])
            sub_history.append(stock_history_list[i][2])
            sub_history.append(stock_history_list[i][3])
            sub_history.append(stock_history_list[i][4])
            sub_history.append(stock_history_list[i][5])
            sub_history_list.append(sub_history)
            data_count+=1
            if data_count >= config.lstm_data_size:
                sub_history_list = reverse(sub_history_list)
                break

    start_collect = False
    data_count = 0
    for i in range(len(stock_price_list)-1,-1,-1):
        price_date = stock_price_list[i][1]
        if date == price_date:
            start_collect = True
        if start_collect:
            sub_price = []
            sub_price.append(stock_price_list[i][0])
            sub_price_list.append(sub_price)
            data_count+=1
            if data_count >= config.lstm_data_size:
                sub_price_list = reverse(sub_price_list)
                break
        
    print "percent after start_collect: %.2f%%" % (p1.memory_percent())

    #标准化
    normalized_stock_history_list = (sub_history_list - np.mean(sub_history_list,axis=0)) / np.std(sub_history_list,axis=0)
    normalized_stock_price_list = (sub_price_list - np.mean(sub_price_list,axis=0)) / np.std(sub_price_list,axis=0)

    print "percent after normalized: %.2f%%" % (p1.memory_percent())

    #训练集输入
    train_x = []
    #训练集输出
    train_y = []

    batch_index = []

    gc.collect()

    for i in range(len(normalized_stock_history_list) - time_step):
        if i % batch_size==0:
            batch_index.append(i)
        x=normalized_stock_history_list[i:i+time_step,:6]
        #print(x)
        y=normalized_stock_price_list[i:i+time_step,0,np.newaxis]
       
        #print(y)
        train_x.append(x.tolist())
        train_y.append(y.tolist())

    batch_index.append((len(normalized_stock_history_list)-time_step))

    
    print "percent after batch_index: %.2f%%" % (p1.memory_percent())

    return batch_index,train_x,train_y



def reverse(arr):
    reverse_arr = []
    for i in range(len(arr)-1,-1,-1):
        reverse_arr.append(arr[i])
    return reverse_arr

'''
#获取训练集
def get_train_data(code,batch_size,time_step,term,date):
    stock_history_list = []
    stock_price_list = []
    cursor.execute(''.join([
            'SELECT ',
            '    * ',
            'FROM ',
            '    ( ',
            '        SELECT ',
            '            t.trade_num, ',
            '            t.trade_money, ',
            '            t.fq_close_price, ',
            '            t.turnover_rate, ',
            '            t.total_value, ',
            '            t.circulation_value, ',
            '            a.future_price_'+term+', ',
            '            t.date ',
            '        FROM ',
            '            stock_history t ',
            '        INNER JOIN stock_train_data a ON a.`code` = t.`code` ',
            '        AND a.date = t.date ',
            '        WHERE ',
            '            t.date <= %s ',
            '        AND t.`code` = %s ',
            '        ORDER BY ',
            '            t.date DESC ',
            '        LIMIT 0, ',
            '        '+ str(config.lstm_data_size) + ' ',
            '    ) tt ',
            'ORDER BY ',
            '    tt.date ASC '
        ]) , [date,code])
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
        #circulation_value:14
        if result[5] is None:
            continue
        stock_history.append(result[5])
        


        if result[6] is None:
            continue
        stock_price.append(result[6])
        
        stock_history_list.append(stock_history)
        stock_price_list.append(stock_price)



    conn.commit()

    #标准化
    normalized_stock_history_list = (stock_history_list - np.mean(stock_history_list,axis=0)) / np.std(stock_history_list,axis=0)
    normalized_stock_price_list = (stock_price_list - np.mean(stock_price_list,axis=0)) / np.std(stock_price_list,axis=0)

    #训练集输入
    train_x = []
    #训练集输出
    train_y = []

    batch_index=[]
    for i in range(len(normalized_stock_history_list) - time_step):
       if i % batch_size==0:
           batch_index.append(i)
       x=normalized_stock_history_list[i:i+time_step,:6]
       #print(x)
       y=normalized_stock_price_list[i:i+time_step,0,np.newaxis]
       
       #print(y)
       train_x.append(x.tolist())
       train_y.append(y.tolist())

    batch_index.append((len(normalized_stock_history_list)-time_step))
    return batch_index,train_x,train_y
'''


def train_lstm(code,batch_size,time_step,term,begin,end):
    
    with tf.variable_scope(code + '_' + term, reuse=None):
        X=tf.placeholder(tf.float32, shape=[None,time_step,input_size])
        Y=tf.placeholder(tf.float32, shape=[None,time_step,output_size])
        weights={
             'in':tf.Variable(tf.random_normal([input_size,rnn_unit])),
             'out':tf.Variable(tf.random_normal([rnn_unit,1]))
            }
        biases={
                'in':tf.Variable(tf.constant(0.1,shape=[rnn_unit,])),
                'out':tf.Variable(tf.constant(0.1,shape=[1,]))
               }
        batch_size=tf.shape(X)[0]
        time_step_tensor=tf.shape(X)[1]
        w_in=weights['in']
        b_in=biases['in']  
        input=tf.reshape(X,[-1,input_size])  #需要将tensor转成2维进行计算，计算后的结果作为隐藏层的输入
        input_rnn=tf.matmul(input,w_in)+b_in
        input_rnn=tf.reshape(input_rnn,[-1,time_step_tensor,rnn_unit])  #将tensor转成3维，作为lstm cell的输入
        cell=tf.nn.rnn_cell.BasicLSTMCell(rnn_unit)
        init_state=cell.zero_state(batch_size,dtype=tf.float32)
        output_rnn,final_states=tf.nn.dynamic_rnn(cell, input_rnn,initial_state=init_state, dtype=tf.float32)
        output=tf.reshape(output_rnn,[-1,rnn_unit]) #作为输出层的输入
        w_out=weights['out']
        b_out=biases['out']
        pred=tf.matmul(output,w_out)+b_out

        #损失函数
        loss=tf.reduce_mean(tf.square(tf.reshape(pred,[-1])-tf.reshape(Y, [-1])))
        train_op=tf.train.AdamOptimizer(lr).minimize(loss)
        saver=tf.train.Saver(tf.global_variables(),max_to_keep=0)
        with tf.Session() as sess:
            sess.run(tf.global_variables_initializer())

            code_path = '/home/ayesha/data/models/'+code
            model_path = code_path + '/' + term
            if not os.path.exists(code_path):
                os.mkdir(code_path)

            if not os.path.exists(model_path):
                os.mkdir(model_path)

            
            begindate = datetime.datetime(int(begin[0:4]),int(begin[5:7]),int(begin[8:10]))
            enddate = datetime.datetime(int(end[0:4]),int(end[5:7]),int(end[8:10]))
            train_count = 0

            stock_history_list,stock_price_list = get_all_train_data(code,term,begin,end)

            while begindate < enddate:
                date = begindate.strftime('%Y-%m-%d')
                #print "percent: %.2f%%" % (p1.memory_percent())
                batch_index,train_x,train_y=get_train_data(stock_history_list,stock_price_list,batch_size,time_step,term,date)
                #print "percent after get_train_data: %.2f%%" % (p1.memory_percent())
                print('training data begin with '+date + ', size = ' + str(config.lstm_data_size))
                for step in range(len(batch_index)-1):
                    final_states,loss_=sess.run([train_op,loss],feed_dict={X:train_x[batch_index[step]:batch_index[step+1]],Y:train_y[batch_index[step]:batch_index[step+1]]})
                #print "percent after training: %.2f%%" % (p1.memory_percent())
                if train_count != 0 and train_count % 200 == 0:
                    print("save model : ", saver.save(sess, model_path + '/stock.model',global_step=train_count))
                begindate += datetime.timedelta(days=1)
                train_count += 1

            print("save model : ", saver.save(sess, model_path + '/stock.model',global_step=train_count))

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
    train_lstm('600000',30 , 30 , '30' , '2005-01-01' , '2005-01-31')
    #train( 30 , 30 , '30' , '2005-01-01' , '2005-01-01' )
    #train( 90 , 90 , '90' , '2005-01-01' , '2005-01-01' )
    #train( 180 , 180 , '180' , '2005-01-01' , '2005-01-01' )
    #train( 360 , 360 , '360' , '2005-01-01' , '2005-01-01' )
    db_close()