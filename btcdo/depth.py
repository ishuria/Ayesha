#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 获取指定交易对深度
import config
import ssl
import requests
import json

def depth():
    ssl._create_default_https_context = ssl._create_unverified_context
    url = config.api_url+"/v1/market/depth/"+config.symbol
    response = config.session.get(url=url,headers=config.headers)
    price_data = json.loads(response.text)
    buy_orders = price_data['buyOrders']
    sell_orders = price_data['sellOrders']
    return buy_orders[0]['price'],buy_orders[0]['amount'],sell_orders[0]['price'],sell_orders[0]['amount']

if __name__ == '__main__':
    buy_one_price,buy_one_amount,sell_one_price,sell_one_amount = depth()
    print('buy_one_price = ' + str(buy_one_price))
    print('buy_one_amount = ' + str(buy_one_amount))
    print('sell_one_price = ' + str(sell_one_price))
    print('sell_one_amount = ' + str(sell_one_amount))

