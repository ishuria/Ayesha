#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import config
import ssl
import requests
import json

def asset():
    ssl._create_default_https_context = ssl._create_unverified_context
    url = 'https://www.coinsuper.com/web/v2/asset/user/getUserAsset'
    params = {"lang": "zh-CN", "data": {"source": "WEB"}}
    response = config.session.post(url,json.dumps(params),verify=True,headers=config.headers)
    print(response.text)

if __name__ == '__main__':
    asset()
