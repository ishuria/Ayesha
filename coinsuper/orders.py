#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 获取指定交易对深度
import config
import ssl
import depth
import time
import uuid
import json
import hmac
import hashlib

def order():
    ssl._create_default_https_context = ssl._create_unverified_context
    url = config.api_url+"/v1/trade/orders"
    buy_one_price,buy_one_amount,sell_one_price,sell_one_amount = depth.depth()

    params = {}
    params['amount'] = config.amount
    params['orderType'] = 'BUY_LIMIT'
    params['price'] = buy_one_price
    params['symbol'] = config.symbol

    param_list = ['%s=%s' % (k, v) for k, v in params.items()]
    param_list.sort()
    payload = ['POST', 'api.btcdo.com', '/v1/trade/orders', '&'.join(param_list)]
    headers = {
        'API-Key': config.api_key,
        'API-Signature-Method': 'HmacSHA256',
        'API-Signature-Version': '1',
        'API-Timestamp': str(int(time.time() * 1000))
    }

    headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'


    headers['API-Unique-ID'] = uuid.uuid4().hex
    headers_list = ['%s: %s' % (k.upper(), v) for k, v in headers.items()]
    headers_list.sort()
    payload.extend(headers_list)
    payload.append(json.dumps(params))
    payload_str = '\n'.join(payload)
    # payload_str += '\n<json body data>'

    # signature:

    # signature = HmacSHA256(payload_str.encode("UTF-8"), config.secret_key) 

    sign = hmac.new(config.secret_key.encode('utf-8'), payload_str.encode('utf-8'), hashlib.sha256).hexdigest()
    print('payload:\n----\n' + payload_str + '----\nsignature: ' + sign)
    headers['API-Signature'] = sign


    response = config.session.post(url=url,params=params,headers=headers)
    print(response.text)

if __name__ == '__main__':
    order()
