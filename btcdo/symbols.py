#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 获取所有交易对
import config
import ssl
import requests

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
session = requests.session()

def symbols():
    ssl._create_default_https_context = ssl._create_unverified_context
    url = config.api_url+"/v1/common/symbols"
    response = session.get(url=url,headers=headers)
    print(response.text)

if __name__ == '__main__':
    symbols()