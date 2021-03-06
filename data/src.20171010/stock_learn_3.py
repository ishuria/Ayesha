# -*- coding: UTF-8 -*-  
import numpy as np
import tensorflow as tf
import config
import MySQLdb as mdb
import stock_sql
import os
import datetime
import decimal  
import sys

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


init_scale = 0.1        # 相关参数的初始值为随机均匀分布，范围是[-init_scale,+init_scale]
learning_rate = 1.0     # 学习速率,在文本循环次数超过max_epoch以后会逐渐降低
max_grad_norm = 5       # 用于控制梯度膨胀，如果梯度向量的L2模超过max_grad_norm，则等比例缩小
num_layers = 2          # lstm层数
num_steps = 20          # 单个数据中，序列的长度。
hidden_size = 200       # 隐藏层中单元数目
max_epoch = 4           # epoch<max_epoch时，lr_decay值=1,epoch>max_epoch时,lr_decay逐渐减小
max_max_epoch = 13      # 指的是整个文本循环次数。
keep_prob = 1.0         # 用于dropout.每批数据输入时神经网络中的每个单元会以1-keep_prob的概率不工作，可以防止过拟合
lr_decay = 0.5          # 学习速率衰减
batch_size = 20         # 每批数据的规模，每批有20个。
vocab_size = 10000      # 词典规模，总共10K个词



#获取训练集，取得输入日期前的数据，数量上限由参数config.lstm_data_size决定
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
        x = stock_history_arr[i:i+time_step,:6]
        y = stock_price_arr[i:i+time_step,0,np.newaxis]
       
        train_x.append(x.tolist())
        train_y.append(y.tolist())

    batch_index.append((len(stock_history_arr)-time_step))
    return batch_index,train_x,train_y


'''
def train_lstm(code,batch_size,time_step,term,begin,end):
    with tf.variable_scope(code + '_' + term, reuse=None):
        code_path = '/home/ayesha/data/models/'+code
        model_path = code_path + '/' + term
        if not os.path.exists(code_path):
            os.mkdir(code_path)

        if not os.path.exists(model_path):
            os.mkdir(model_path)

        model_file = model_path + '/checkpoint'
        model_file_exists = os.path.exists(model_file)

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
        cell=tf.nn.rnn_cell.BasicLSTMCell(rnn_unit,state_is_tuple=True)
        init_state=cell.zero_state(batch_size,dtype=tf.float32)
        output_rnn,final_states=tf.nn.dynamic_rnn(cell, input_rnn,initial_state=init_state, dtype=tf.float32)
        output=tf.reshape(output_rnn,[-1,rnn_unit]) #作为输出层的输入
        w_out=weights['out']
        b_out=biases['out']
        pred=tf.matmul(output,w_out)+b_out

        #损失函数
        loss=tf.reduce_mean(tf.square(tf.reshape(pred[-1],[-1])-tf.reshape(Y[-1], [-1])))

        global_step = tf.Variable(0,name='global_step',trainable=False)
        train_op=tf.train.AdamOptimizer(lr).minimize(loss,global_step=global_step)
        
        enddate = datetime.datetime(int(end[0:4]),int(end[5:7]),int(end[8:10]))
        begindate = datetime.datetime(int(begin[0:4]),int(begin[5:7]),int(begin[8:10]))

        
        
        with tf.Session() as sess:
            saver=tf.train.Saver()
            sess.run(tf.global_variables_initializer())

            while begindate <= enddate:
                date = begindate.strftime('%Y-%m-%d')
                batch_index,train_x,train_y = get_train_data(code,batch_size,time_step,term,date)
                for step in range(len(batch_index)-1):
                    final_states,loss_=sess.run([train_op,loss],feed_dict={X:train_x[batch_index[step]:batch_index[step+1]],Y:train_y[batch_index[step]:batch_index[step+1]]})
                print("save model : ", saver.save(sess, model_path + '/stock.model',global_step=global_step) , " date : " , date)

                begindate = begindate + datetime.timedelta(days=1)
'''



def train_lstm_daily(code,batch_size,time_step,term,date):
    with tf.variable_scope(code + '_' + term, reuse=None):
        code_path = '/home/ayesha/data/models/'+code
        model_path = code_path + '/' + term
        if not os.path.exists(code_path):
            os.mkdir(code_path)

        if not os.path.exists(model_path):
            os.mkdir(model_path)

        model_file = model_path + '/checkpoint'
        model_file_exists = os.path.exists(model_file)

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
        batch_size_tensor=tf.shape(X)[0]
        time_step_tensor=tf.shape(X)[1]
        w_in=weights['in']
        b_in=biases['in']  
        input=tf.reshape(X,[-1,input_size])  #需要将tensor转成2维进行计算，计算后的结果作为隐藏层的输入
        input_rnn=tf.matmul(input,w_in)+b_in
        input_rnn=tf.reshape(input_rnn,[-1,time_step_tensor,rnn_unit])  #将tensor转成3维，作为lstm cell的输入
        cell = tf.nn.rnn_cell.BasicLSTMCell(rnn_unit,state_is_tuple=True)

        init_state=cell.zero_state(batch_size_tensor,dtype=tf.float32)
        output_rnn,final_states=tf.nn.dynamic_rnn(cell, input_rnn,initial_state=init_state, dtype=tf.float32)
        output=tf.reshape(output_rnn,[-1,rnn_unit]) #作为输出层的输入
        w_out=weights['out']
        b_out=biases['out']
        pred=tf.matmul(output,w_out)+b_out

        #损失函数
        loss=tf.reduce_mean(tf.square(tf.reshape(pred,[-1])-tf.reshape(Y, [-1])))

        global_step = tf.Variable(0,name='global_step',trainable=False)
        train_op=tf.train.AdamOptimizer(lr).minimize(loss,global_step=global_step)
        
        batch_index,train_x,train_y = get_train_data(code,batch_size,time_step,term,date)
        saver=tf.train.Saver()
        with tf.Session() as sess:
            if model_file_exists:
                module_file = tf.train.latest_checkpoint(model_path)
                saver.restore(sess, module_file)
                print('restore model')
            else:
                sess.run(tf.global_variables_initializer())
                print('initialize model')

            for step in range(len(batch_index)-1):
                final_states,loss_=sess.run([train_op,loss],feed_dict={X:train_x[batch_index[step]:batch_index[step+1]],Y:train_y[batch_index[step]:batch_index[step+1]]})
            print("save model : ", saver.save(sess, model_path + '/stock.model',global_step=global_step) , " date : " , date)

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
    #train_lstm('600000',30 , 30 , '30' , '2005-01-01' , '2012-12-31')
    ''''''
    code = sys.argv[1]
    batch_size = sys.argv[2]
    time_step = sys.argv[3]
    term = sys.argv[4]
    date = sys.argv[5]
    train_lstm_daily(code,int(batch_size) , int(time_step) , term , date )
    
    #train( 30 , 30 , '30' , '2005-01-01' , '2012-12-31' )
    #train( 90 , 90 , '90' , '2005-01-01' , '2005-01-01' )
    #train( 180 , 180 , '180' , '2005-01-01' , '2005-01-01' )
    #train( 360 , 360 , '360' , '2005-01-01' , '2005-01-01' )
    db_close()
