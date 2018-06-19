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
trade_pair=cp.get('BASE_CONF','TRADE_PAIR')

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


    return buy_price,sell_price

def trade_history():
    ssl._create_default_https_context = ssl._create_unverified_context
    url = "https://btex.com/api1/trades?pair="+trade_pair+""
    response = session.post(url,[],verify=True)
    print(response.text)

def login():
    ssl._create_default_https_context = ssl._create_unverified_context
    url = "https://btex.com/pubapi1/user_login"
    values = {}
    values['email_mobile'] = 'candy_20180509@163.com'
    values['psw'] = 'candy20180509'
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
    values['trade_psw'] = 'btex20180619'
    
    #临时解决https的问题
    response = session.post(url,values,verify=True)
    print(response.text)

def trade_eth_tco():
    response = session.post('https://btex.com/trade/'+trade_pair,[],verify=True)
    p = re.compile(r'<input type=\"hidden\" id=\"csrf\" value=\"(.+?)\" />')
    m = p.search(response.text)
    print(m.group())
    csrf = m.group()[38:70]

    url = "https://btex.com/priapi1/buy_coin"
    values = {}
    values['price'] = 0.00000800
    values['num'] = 1000
    values['type'] = 'TCO'
    values['danwei'] = 'ETH'
    values['csrf'] = csrf
    values['trade_psw'] = 'btex20180619'
    
    #临时解决https的问题
    response = session.post(url,values,verify=True)
    print(response.text)

def trade_tco_eth():
    response = session.post('https://btex.com/trade/'+trade_pair,[],verify=True)
    p = re.compile(r'<input type=\"hidden\" id=\"csrf\" value=\"(.+?)\" />')
    m = p.search(response.text)
    print(m.group())
    csrf = m.group()[38:70]

    url = "https://btex.com/priapi1/sell_coin"
    values = {}
    values['price'] = 0.00000800
    values['num'] = 1000
    values['type'] = 'TCO'
    values['danwei'] = 'ETH'
    values['csrf'] = csrf
    values['trade_psw'] = 'btex20180619'
    
    #临时解决https的问题
    response = session.post(url,values,verify=True)
    print(response.text)

if __name__ == '__main__':
    # login()
    # trade()
    # post_price()
    # post_trade()



    login()
    buy_price,sell_price = order_book()
    while buy_price < sell_price:
        trade_eth_tco()
        trade_tco_eth()
        buy_price,sell_price = order_book()


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