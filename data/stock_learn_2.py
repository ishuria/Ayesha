# -*- coding: UTF-8 -*-  
import numpy as np
import tensorflow as tf
import config
import MySQLdb as mdb
import stock_sql
import os


#学习开始年份
LEARNING_YEAR_START = '2014'
#学习结束年份
LEARNING_YEAR_END = '2014'
#验证年份
VALIDATION_YEAR = '2015'
#市场
markets = ['sh','sz']


#定义常量
rnn_unit=10
input_size=6
output_size=1
#学习率
lr=0.0006


conn = None
cursor = None


#获取训练集
def get_train_data(code,batch_size=60,time_step=20,begin='2010-01-01',end='2014-12-31'):
    global conn
    global cursor
    stock_history_list = []
    stock_price_list = []
    cursor.execute(''.join([
            'SELECT ',
            't.trade_num, ',
            't.trade_money, ',
            't.fq_close_price, ',
            't.turnover_rate, ',
            't.total_value, ',
            't.circulation_value, ',
            'a.future_price_30, ',
            'a.future_price_90, ',
            'a.future_price_180, ',
            'a.future_price_360 ',
            'FROM ',
            '    stock_history t ',
            'INNER JOIN stock_train_data a ON a.`code` = t.`code` ',
            'AND a.date = t.date ',
            'WHERE ',
            '    t.date >= %s ',
            'AND t.date <= %s ',
            'AND t.`code` = %s ',
            'ORDER BY t.date ASC '
        ]) , [begin,end,code])
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
        stock_price.append(result[7])
        if result[8] is None:
            continue
        stock_price.append(result[8])
        if result[9] is None:
            continue
        stock_price.append(result[9])
        
        stock_history_list.append(stock_history)
        stock_price_list.append(stock_price)



    conn.commit()

    #标准化
    normalized_stock_history_list = (stock_history_list - np.mean(stock_history_list,axis=0)) / np.std(stock_history_list,axis=0)
    normalized_stock_price_list = (stock_price_list - np.mean(stock_price_list,axis=0)) / np.std(stock_price_list,axis=0)

    #训练集输入
    train_x = []
    #训练集输出
    train_y_30 = []
    train_y_90 = []
    train_y_180 = []
    train_y_360 = []

    batch_index=[]
    for i in range(len(normalized_stock_history_list) - time_step):
       if i % batch_size==0:
           batch_index.append(i)
       x=normalized_stock_history_list[i:i+time_step,:6]
       #print(x)
       y_30=normalized_stock_price_list[i:i+time_step,0,np.newaxis]
       y_90=normalized_stock_price_list[i:i+time_step,1,np.newaxis]
       y_180=normalized_stock_price_list[i:i+time_step,2,np.newaxis]
       y_360=normalized_stock_price_list[i:i+time_step,3,np.newaxis]
       
       #print(y)
       train_x.append(x.tolist())
       train_y_30.append(y_30.tolist())
       train_y_90.append(y_90.tolist())
       train_y_180.append(y_180.tolist())
       train_y_360.append(y_360.tolist())

    batch_index.append((len(normalized_stock_history_list)-time_step))
    return batch_index,train_x,train_y_30,train_y_90,train_y_180,train_y_360




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


def train_lstm_sub(code,batch_index,train_x,train_y,term,batch_size=80,time_step=15,begin='2010-01-01',end='2014-12-31'):
    with tf.variable_scope(code + '_' + term, reuse=None):
        X=tf.placeholder(tf.float32, shape=[None,time_step,input_size])
        Y=tf.placeholder(tf.float32, shape=[None,time_step,output_size])
        pred,_=lstm(X)
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

            #训练30天数据
            for i in range(2001):
                for step in range(len(batch_index)-1):
                    _,loss_=sess.run([train_op,loss],feed_dict={X:train_x[batch_index[step]:batch_index[step+1]],Y:train_y[batch_index[step]:batch_index[step+1]]})
                if i % 200==0:
                    print("save model : ", saver.save(sess, model_path + '/stock.model',global_step=i))



#训练模型，对每一只股票单独建立模型
def train_lstm(code,batch_size=80,time_step=15,begin='2010-01-01',end='2014-12-31'):
    batch_index,train_x,train_y_30,train_y_90,train_y_180,train_y_360=get_train_data(code,batch_size,time_step,begin,end)
    train_lstm_sub( code, batch_index, train_x, train_y_30, '30', batch_size, time_step, begin, end)
    train_lstm_sub( code, batch_index, train_x, train_y_90, '90', batch_size, time_step, begin, end)
    train_lstm_sub( code, batch_index, train_x, train_y_180, '180', batch_size, time_step, begin, end)
    train_lstm_sub( code, batch_index, train_x, train_y_360, '360', batch_size, time_step, begin, end)

#训练函数
def train(batch_size,time_step,begin,end):
    global conn
    global cursor
    conn = mdb.connect(host=config.mysql_ip, port=config.mysql_port,user=config.mysql_user,passwd=config.mysql_pass,db=config.mysql_db,charset='utf8')
    cursor = conn.cursor()

    for market in markets:
        code_list = getCodeList(market)
        for code in code_list:
            train_lstm(code,batch_size,time_step,begin,end)

    #关闭数据库连接
    cursor.close()
    conn.close()

def getCodeList(market):
    global conn
    global cursor
    stock_list = []
    cursor.execute(stock_sql.stock_market_select_sql , [market])
    results = cursor.fetchall()
    for result in results:
        stock_list.append(result[6])
    return stock_list

if __name__ == '__main__':
    train(80,15,'2005-01-01','2014-12-31')