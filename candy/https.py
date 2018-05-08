#-*-coding:utf-8-*-
# Time:2017/9/25 20:41
# Author:YangYangJun

import requests
import ssl
from requests.auth import HTTPBasicAuth

import cell_num


def post_login():

    url = "https://www.url"
    values = {}
    values['username'] = 'username'
    values['password'] = 'password'
    response = requests.post(url,values)
    print (response.text)



def get_login():
    url = "https://www.url"
    values = {}
    values['username'] = 'username'
    values['password'] = 'password'
    #geturl = url + '?' + values
    response = requests.get(url, values)
    print (response.content)


def post_loginHttps1():

    url = "https://candy.one/api/user/is_register"
    values = {}
    values['phone'] = '+8615544231123'
    values['country_code'] = 'cn'
    #临时解决https的方法1
    response = requests.post(url,values,verify=False)
    print (response.text)

def post_loginHttps2():
    #解决https方法2
    ssl._create_default_https_context = ssl._create_unverified_context

    url = "https://candy.one/api/user/is_register"
    values = {}
    values['phone'] = '+8615544231123'
    values['country_code'] = 'cn'
    #临时解决https的问题
    response = requests.post(url,values,verify=True)
    print(response.text)


def post_signup():
    #解决https方法2
    ssl._create_default_https_context = ssl._create_unverified_context

    url = "https://candy.one/api/passport/signup"
    #{phone: "+8613465217567", country_code: "cn", password: "123456", inviter_id: "4325572"}
    values = {}
    values['phone'] = '+86'+cell_num.gen_random_cell_num()
    values['country_code'] = 'cn'
    values['password'] = '123456'
    values['inviter_id'] = '4327402'
    #values['inviter_id'] = '4325572'
    
    #临时解决https的问题
    response = requests.post(url,values,verify=True)
    print(response.text)


if __name__ == '__main__':
    #post_login()
    #get_login()
    # post_loginHttps1()
    #post_loginHttps2()
    for i in range(2):
        post_signup()

    #出现下面错误的原因主要是因为打开了fiddler，关闭fiddler即可。

#     raise SSLError(e, request=request)
# requests.exceptions.SSLError: HTTPSConnectionPool(host='www.yiyao.cc', port=443): Max retries exceeded with url: /user/loginWeb (Caused by SSLError(SSLError(1, u'[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed (_ssl.c:661)'),))
#






'''
{phone: "+8613465217567", country_code: "cn"}
Request URL: https://candy.one/api/user/is_register
Request Method: POST
Status Code: 200 
Remote Address: 104.25.94.105:443
Referrer Policy: no-referrer-when-downgrade
access-control-allow-headers: Origin, X-Requested-With, Content-Type, Accept, x-access-token, If-Modified-Since
access-control-allow-origin: *
cf-ray: 4179d8787fa36cc4-SJC
content-encoding: gzip
content-type: application/json; charset=utf-8
date: Tue, 08 May 2018 06:24:50 GMT
etag: W/"41-W9g3jeSFp2T3T42MDCJcv2DrV60"
expect-ct: max-age=604800, report-uri="https://report-uri.cloudflare.com/cdn-cgi/beacon/expect-ct"
server: cloudflare
status: 200
vary: Accept-Encoding
x-request-id: 41dacaea-2f68-4c7b-87d0-43f524160d44
:authority: candy.one
:method: POST
:path: /api/user/is_register
:scheme: https
accept: application/json, text/plain, */*
accept-encoding: gzip, deflate, br
accept-language: zh-CN,zh;q=0.9
content-length: 46
content-type: application/json;charset=UTF-8
cookie: __cfduid=d3eb2e763c680f9999a5b5982ca6f65da1525747026; _uab_collina=152574702889739721939187; _umdata=85957DF9A4B3B3E806170A2E6FB1445E179DAC9D63A5CF2F3D0B9A4D84E484FA8D291FD88D369A6BCD43AD3E795C914C74B244E98D082AD08755F7F01A516FC9; _ga=GA1.2.824773737.1525760651; _gid=GA1.2.347649143.1525760651; _gat_gtag_UA_112996733_1=1; locale_language=zhHans; _candy_invite=4325572
origin: https://candy.one
referer: https://candy.one/i/4325572
user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36





{phone: "+8613465217567", country_code: "cn", password: "123456", inviter_id: "4325572"}
Request URL: https://candy.one/api/passport/signup
Request Method: POST
Status Code: 200 
Remote Address: 104.25.94.105:443
Referrer Policy: no-referrer-when-downgrade
access-control-allow-headers: Origin, X-Requested-With, Content-Type, Accept, x-access-token, If-Modified-Since
access-control-allow-origin: *
cf-ray: 4179d89809286cc4-SJC
content-encoding: gzip
content-type: application/json; charset=utf-8
date: Tue, 08 May 2018 06:24:55 GMT
etag: W/"378-mJWtfzx0mii2UnCCwx53nLEr678"
expect-ct: max-age=604800, report-uri="https://report-uri.cloudflare.com/cdn-cgi/beacon/expect-ct"
server: cloudflare
status: 200
vary: Accept-Encoding
x-request-id: fa0c9f28-9c39-4911-b512-328d35837d6e
:authority: candy.one
:method: POST
:path: /api/passport/signup
:scheme: https
accept: application/json, text/plain, */*
accept-encoding: gzip, deflate, br
accept-language: zh-CN,zh;q=0.9
content-length: 89
content-type: application/json;charset=UTF-8
cookie: __cfduid=d3eb2e763c680f9999a5b5982ca6f65da1525747026; _uab_collina=152574702889739721939187; _umdata=85957DF9A4B3B3E806170A2E6FB1445E179DAC9D63A5CF2F3D0B9A4D84E484FA8D291FD88D369A6BCD43AD3E795C914C74B244E98D082AD08755F7F01A516FC9; _ga=GA1.2.824773737.1525760651; _gid=GA1.2.347649143.1525760651; _gat_gtag_UA_112996733_1=1; locale_language=zhHans; _candy_invite=4325572; _candy_phone=+8613465217567; _candy_country_code=cn
origin: https://candy.one
referer: https://candy.one/i/4325572
user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36
'''