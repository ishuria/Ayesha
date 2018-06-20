import random
import requests
import ssl
from requests.auth import HTTPBasicAuth
import configparser
import time
import traceback
import re
import json


cp=configparser.ConfigParser()
cp.read("btex.ini")
#交易对
trade_pair = cp.get('BASE_CONF','TRADE_PAIR')
base_coin = trade_pair.split('_')[1]
target_coin = trade_pair.split('_')[0]
account = cp.get('BASE_CONF','ACCOUNT')
password = cp.get('BASE_CONF','PASSWORD')
trade_password = cp.get('BASE_CONF','TRADE_PASSWORD')
trade_num = cp.get('TRADE_CONF','TRADE_NUM')

#全局session
session = requests.session()

proxies = { "http": "http://10.10.1.10:3128", "https": "http://127.0.0.1:1080", } 

def post_trade():
    ssl._create_default_https_context = ssl._create_unverified_context
    url = "https://btex.com/api1/trades?pair=BT_ETH"    
    response = session.post(url,[],verify=True)
    print(response.text)

def post_price():
    ssl._create_default_https_context = ssl._create_unverified_context
    url = "https://btex.com/api1/k_data/?pair=ETD_DOGE&k_type=5m&rand_key=32320339"
    response = session.post(url,[],verify=True)
    print(response.text)

def order_book():
    ssl._create_default_https_context = ssl._create_unverified_context
    url = "https://btex.com/api1/orderbook?pair="+trade_pair+"&depth=15"
    response = session.post(url,[],verify=True)
    # print(response.text)
    response_data = json.loads(response.text)
    buy_data = response_data['data']['buy']
    sell_data = response_data['data']['sell']

    buy_price = buy_data[0]['price']
    sell_price = sell_data[0]['price']


    return float(buy_price),float(sell_price)

def trade_history():
    ssl._create_default_https_context = ssl._create_unverified_context
    url = "https://btex.com/api1/trades?pair="+trade_pair+""
    response = session.post(url,[],verify=True)
    print(response.text)

def login():
    ssl._create_default_https_context = ssl._create_unverified_context
    url = "https://btex.com/pubapi1/user_login"
    values = {}
    values['email_mobile'] = account
    values['psw'] = password
    values['auth_num'] = ''
    values['check_pic'] = ''
    response = session.post(url,values,verify=True)
    print(response.text)

def trade():
    response = session.post('https://btex.com/trade/'+trade_pair,[],verify=True)
    p = re.compile(r'<input type=\"hidden\" id=\"csrf\" value=\"(.+?)\" />')
    m = p.search(response.text)
    print(m.group())
    csrf = m.group()[38:70]

    url = "https://btex.com/priapi1/buy_coin"
    values = {}
    values['price'] = 0.00000900
    values['num'] = 2000
    values['type'] = 'TCO'
    values['danwei'] = 'ETH'
    values['csrf'] = csrf
    values['trade_psw'] = trade_password
    
    #临时解决https的问题
    response = session.post(url,values,verify=True)
    print(response.text)

def trade_eth_tco(csrf,price,num):
    # response = session.post('https://btex.com/trade/'+trade_pair,[],verify=True)
    # p = re.compile(r'<input type=\"hidden\" id=\"csrf\" value=\"(.+?)\" />')
    # m = p.search(response.text)
    # print(m.group())
    # csrf = m.group()[38:70]

    url = "https://btex.com/priapi1/buy_coin"
    values = {}
    values['price'] = price
    values['num'] = num
    values['type'] = target_coin
    values['danwei'] = base_coin
    values['csrf'] = csrf
    values['trade_psw'] = trade_password
    
    #临时解决https的问题
    response = session.post(url,values,verify=True)
    print(response.text)
    response_data = json.loads(response.text)
    return response_data['info']

def trade_tco_eth(csrf,price,num):
    # response = session.post('https://btex.com/trade/'+trade_pair,[],verify=True)
    # p = re.compile(r'<input type=\"hidden\" id=\"csrf\" value=\"(.+?)\" />')
    # m = p.search(response.text)
    # print(m.group())
    # csrf = m.group()[38:70]

    url = "https://btex.com/priapi1/sell_coin"
    values = {}
    values['price'] = price
    values['num'] = num
    values['type'] = target_coin
    values['danwei'] = base_coin
    values['csrf'] = csrf
    values['trade_psw'] = trade_password
    
    #临时解决https的问题
    response = session.post(url,values,verify=True)
    print(response.text)

    response_data = json.loads(response.text)
    return response_data['info']

def get_csrf():
    response = session.post('https://btex.com/trade/'+trade_pair,[],verify=True)
    p = re.compile(r'<input type=\"hidden\" id=\"csrf\" value=\"(.+?)\" />')
    m = p.search(response.text)
    print(m.group())
    csrf = m.group()[38:70]
    return csrf

def get_rand_price(buy_price,sell_price):
    return (buy_price*1000000000 + 10) / 1000000000
    # low_price = sell_price*1000000000*0.95
    # return float(random.randint(int(low_price),sell_price*1000000000) ) / 1000000000

if __name__ == '__main__':
    # login()
    # trade()
    # post_price()
    # post_trade()



    login()
    csrf = get_csrf()
    buy_price,sell_price = order_book()
    # print(buy_price,sell_price)
    # count  = 1
    trade_price = get_rand_price(buy_price,sell_price)
    buy_info = 'Operation Successfully'
    sell_info = 'Operation Successfully'

    while buy_price < sell_price and buy_info == 'Operation Successfully' and sell_info == 'Operation Successfully' and (trade_price > buy_price and trade_price < sell_price):
        buy_info = trade_eth_tco(csrf,trade_price,trade_num)
        sell_info = trade_tco_eth(csrf,trade_price,trade_num)
        time.sleep(0.2)
        buy_price,sell_price = order_book()
        trade_price = get_rand_price(buy_price,sell_price)
        # count = count + 1
        print(buy_price,sell_price,trade_price)


    # trade_history()
    # buy_coin()
    # while(True):
    #     try:
    #         main()
    #     except Exception as e:
    #         print ('str(Exception):\t', str(Exception))
    #         print ('str(e):\t\t', str(e))
    #         print ('repr(e):\t', repr(e))
    #         #print ('e.message:\t', e.message)
    #         print ('traceback.print_exc():', traceback.print_exc())
    #         print ('traceback.format_exc():\n%s' % traceback.format_exc())
    #     print("sleep")
    #     time.sleep(1)