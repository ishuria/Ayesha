import random
import requests
import ssl
from requests.auth import HTTPBasicAuth
import configparser
import time
import traceback
import re

proxies = { "http": "http://10.10.1.10:3128", "https": "http://127.0.0.1:1080", } 

cp=configparser.ConfigParser()

def get_last_phone_num():
    cp.read("phone_num.ini")
    area_num=cp.get('phonenumconf','area_num')
    current_num=cp.get('phonenumconf','current_num')
    phone_num = area_num + current_num
    return phone_num
    
def save_last_phone_num(phone_num):
    current_num = str(phone_num)[3:9]
    cp.set('phonenumconf','current_num',current_num)
    cp.write(open("phone_num.ini",'w'))

def main():
    phone_num = get_last_phone_num()
    #调用注册函数
    post_signup(phone_num,"123456","23571306","my")
    phone_num=int(phone_num)+1
    save_last_phone_num(phone_num)

def post_signup(phone_num,password,inviter_id,country_code):
    #解决https方法2
    ssl._create_default_https_context = ssl._create_unverified_context

    url = "https://candy.one/api/passport/signup"
    #{phone: "+8613465217567", country_code: "cn", password: "123456", inviter_id: "4325572"}
    values = {}
    values['phone'] = '+60'+phone_num
    values['country_code'] = country_code
    values['password'] = password
    values['inviter_id'] = inviter_id
    #values['inviter_id'] = '4325572'
    
    #临时解决https的问题
    response = requests.post(url,values,verify=True)
    print(response.text)


def post_trade():
    #解决https方法2
    ssl._create_default_https_context = ssl._create_unverified_context

    url = "https://btex.com/api1/trades?pair=BT_ETH"
    
    #临时解决https的问题
    response = requests.post(url,[],verify=True)
    print(response.text)


def post_price():
    #解决https方法2
    ssl._create_default_https_context = ssl._create_unverified_context

    url = "https://btex.com/api1/k_data/?pair=ETD_DOGE&k_type=5m&rand_key=32320339"
    
    #临时解决https的问题
    response = requests.post(url,[],verify=True)
    print(response.text)

def buy_coin():
    #解决https方法2
    ssl._create_default_https_context = ssl._create_unverified_context

    url = "https://btex.com/priapi1/buy_coin"
    values = {}
    values['price'] = 0.001
    values['num'] = 1.1523
    values['type'] = 'BT'
    values['danwei'] = 'ETH'
    values['csrf'] = '89ea2a16edd2772320eb719f27c265da'
    values['trade_psw'] = 'btex201806191'
    
    #临时解决https的问题
    response = requests.post(url,values,verify=True)
    print(response.text)


def login():
    #解决https方法2
    ssl._create_default_https_context = ssl._create_unverified_context

    url = "https://btex.com/pubapi1/user_login"
    values = {}
    values['email_mobile'] = 'candy_20180509@163.com'
    values['psw'] = 'candy20180509'
    values['auth_num'] = ''
    values['check_pic'] = ''
    
    #临时解决https的问题
    s = requests.session()
    response = s.post(url,values,verify=True)
    print(response.text)


    response = s.post('https://btex.com/trade/BT_ETH',[],verify=True)

    p = re.compile(r'<input type=\"hidden\" id=\"csrf\" value=\"(.+?)\" />')
    m = p.search(response.text)
    print(m.group())

    # print(type(m.group()))
    # print(m.group()[38:70])
    csrf = m.group()[38:70]

    # print(response.text)

    

    url = "https://btex.com/priapi1/buy_coin"
    values = {}
    values['price'] = 0.001
    values['num'] = 1.1523
    values['type'] = 'BT'
    values['danwei'] = 'ETH'
    values['csrf'] = csrf
    values['trade_psw'] = 'btex201806191'
    
    #临时解决https的问题
    response = s.post(url,values,verify=True)
    print(response.text)


if __name__ == '__main__':
    login()
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