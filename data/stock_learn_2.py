# -*- coding: UTF-8 -*-  
import numpy as np
import tensorflow as tf
import config
import MySQLdb as mdb


#学习开始年份
LEARNING_YEAR_START = '2014'
#学习结束年份
LEARNING_YEAR_END = '2014'
#验证年份
VALIDATION_YEAR = '2015'
#市场
MARKETS = ['sh','sz']




#定义常量
rnn_unit=10       #hidden layer units
input_size=6
output_size=1
#学习率
lr=0.0006






#获取训练集
def get_train_data(code,batch_size=60,time_step=20,train_begin_year='2010',train_end_year='2014'):
    date_begin = train_begin_year + '-01-01'
    date_end = train_end_year + '-12-31'
    conn = mdb.connect(host=config.mysql_ip, port=config.mysql_port,user=config.mysql_user,passwd=config.mysql_pass,db=config.mysql_db,charset='utf8')
    cursor = conn.cursor()
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
            'AND t.`code` = %s '
        ]) , [date_begin,date_end,code])
    results = cursor.fetchall()
    for result in results:
        stock_history = []
        stock_price = []
        #trade_num:2
        stock_history.append(result[0])
        #trade_money:3
        stock_history.append(result[1])
        #close_price:4
        stock_history.append(result[2])
        #turn_over:12
        stock_history.append(result[3])
        #total_value:13
        stock_history.append(result[4])
        #circulation_value:14
        stock_history.append(result[5])
        stock_history_list.append(stock_history)

        #stock_price.append(result[6])
        #stock_price.append(result[7])
        stock_price.append(result[8])
        #stock_price.append(result[9])
        stock_price_list.append(stock_price)



    conn.commit()
    cursor.close()
    conn.close()

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


#获取测试集
def get_test_data(code,time_step=20,train_begin_year='2010',train_end_year='2014'):
    date_begin = train_begin_year + '-01-01'
    date_end = train_end_year + '-12-31'
    conn = mdb.connect(host=config.mysql_ip, port=config.mysql_port,user=config.mysql_user,passwd=config.mysql_pass,db=config.mysql_db,charset='utf8')
    cursor = conn.cursor()
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
            'AND t.`code` = %s '
        ]) , [date_begin,date_end,code])
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
        stock_history_list.append(stock_history)


    conn.commit()
    cursor.close()
    conn.close()





    mean=np.mean(stock_history_list,axis=0)
    std=np.std(stock_history_list,axis=0)
    normalized_test_data=(stock_history_list-mean)/std  #标准化
    size=(len(normalized_test_data)+time_step-1)//time_step  #有size个sample 
    test_x,test_y=[],[]  
    for i in range(size-1):
       x=normalized_test_data[i*time_step:(i+1)*time_step,:6]
       y=normalized_test_data[i*time_step:(i+1)*time_step,0]
       test_x.append(x.tolist())
       test_y.extend(y)
    test_x.append((normalized_test_data[(i+1)*time_step:,:6]).tolist())
    test_y.extend((normalized_test_data[(i+1)*time_step:,0]).tolist())
    return mean,std,test_x,test_y



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
    output_rnn,final_states=tf.nn.dynamic_rnn(cell, input_rnn,initial_state=init_state, dtype=tf.float32)  #output_rnn是记录lstm每个输出节点的结果，final_states是最后一个cell的结果
    output=tf.reshape(output_rnn,[-1,rnn_unit]) #作为输出层的输入
    w_out=weights['out']
    b_out=biases['out']
    pred=tf.matmul(output,w_out)+b_out
    return pred,final_states



#——————————————————训练模型——————————————————
def train_lstm(code,batch_size=80,time_step=15,train_begin_year='2010',train_end_year='2014'):
    X=tf.placeholder(tf.float32, shape=[None,time_step,input_size])
    Y=tf.placeholder(tf.float32, shape=[None,time_step,output_size])
    batch_index,train_x,train_y=get_train_data(code,batch_size,time_step,train_begin_year,train_end_year)
    pred,_=lstm(X)
    #损失函数
    loss=tf.reduce_mean(tf.square(tf.reshape(pred,[-1])-tf.reshape(Y, [-1])))
    train_op=tf.train.AdamOptimizer(lr).minimize(loss)
    saver=tf.train.Saver(tf.global_variables(),max_to_keep=15)
    module_file = tf.train.latest_checkpoint('/home/ayesha/data')
    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        #saver.restore(sess, module_file)
        #重复训练10000次
        for i in range(2000):
            for step in range(len(batch_index)-1):
                _,loss_=sess.run([train_op,loss],feed_dict={X:train_x[batch_index[step]:batch_index[step+1]],Y:train_y[batch_index[step]:batch_index[step+1]]})
            print(i,loss_)
            if i % 200==0:
                print("保存模型：",saver.save(sess,'stock2.model',global_step=i))


#train_lstm()


#————————————————预测模型————————————————————
def prediction(code,time_step=20,train_begin_year='2010',train_end_year='2014'):
    X=tf.placeholder(tf.float32, shape=[None,time_step,input_size])
    #Y=tf.placeholder(tf.float32, shape=[None,time_step,output_size])
    mean,std,test_x,test_y=get_test_data(code,time_step,train_begin_year,train_end_year)
    pred,_=lstm(X)
    saver=tf.train.Saver(tf.global_variables())
    with tf.Session() as sess:
        #参数恢复
        module_file = tf.train.latest_checkpoint('/home/ayesha/data')
        saver.restore(sess, module_file)
        test_predict=[]
        for step in range(len(test_x)-1):
          prob=sess.run(pred,feed_dict={X:[test_x[step]]})
          predict=prob.reshape((-1))
          test_predict.extend(predict)
        test_y=np.array(test_y)*std[2]+mean[2]
        test_predict=np.array(test_predict)*float(std[2])+float(mean[2])
        acc=np.average(np.abs(test_predict-test_y[:len(test_predict)])/test_y[:len(test_predict)])  #偏差
        #以折线图表示结果
        plt.figure()
        plt.plot(list(range(len(test_predict))), test_predict, color='b')
        plt.plot(list(range(len(test_y))), test_y,  color='r')
        #plt.show()
        plt.savefig('/home/ayesha/data/plot1.png', format='png')

#prediction()




if __name__ == '__main__':
    train_lstm('600000',80,15,'2010','2014')
    #prediction('600000',15,'2010','2014')