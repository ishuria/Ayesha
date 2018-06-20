#-*-coding:utf-8-*-
import requests
import configparser
import ssl
import json
import random
#全局session
session = requests.session()

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

def get_balance():
    ssl._create_default_https_context = ssl._create_unverified_context
    url = "https://btex.com/priapi1/my_coins"
    values = {}
    response = session.post(url,values,verify=True)
    print(response.text)

def order_book():
    ssl._create_default_https_context = ssl._create_unverified_context
    url = "https://btex.com/api1/orderbook?pair=XMX_USDT&depth=15"
    response = session.post(url,[],verify=True)
    # print(response.text)
    response_data = json.loads(response.text)
    buy_data = response_data['data']['buy']
    sell_data = response_data['data']['sell']

    buy_price = buy_data[0]['price']
    sell_price = sell_data[0]['price']


    return float(buy_price),float(sell_price)

def get_rand_price(buy_price,sell_price):
    return float(random.randint(buy_price*1000000,sell_price*1000000) ) / 1000000

if __name__ == '__main__':
    login()
    get_balance()
    buy_price ,sell_price = order_book()
    print(get_rand_price(buy_price ,sell_price))

