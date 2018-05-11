import random
import requests
import ssl
from requests.auth import HTTPBasicAuth
import configparser
import time
import traceback

proxies = { "http": "http://10.10.1.10:3128", "https": "http://127.0.0.1:1080", } 

cp=configparser.ConfigParser()

def get_last_phone_num():
    cp.read("phone_num.ini")
    area_num=cp.get('phonenumconf','area_num')
    current_num=cp.get('phonenumconf','current_num')
    phone_num = area_num + current_num
    return phone_num
    
def save_last_phone_num(phone_num):
    current_num = str(phone_num)[3:11]
    cp.set('phonenumconf','current_num',current_num)
    cp.write(open("phone_num.ini",'w'))

def main():
    phone_num = get_last_phone_num()
    #调用注册函数
    post_signup(phone_num,"123456","4640652","cn")
    phone_num=int(phone_num)+1
    save_last_phone_num(phone_num)

def post_signup(phone_num,password,inviter_id,country_code):
    #解决https方法2
    ssl._create_default_https_context = ssl._create_unverified_context

    url = "https://candy.one/api/passport/signup"
    #{phone: "+8613465217567", country_code: "cn", password: "123456", inviter_id: "4325572"}
    values = {}
    values['phone'] = '+86'+phone_num
    values['country_code'] = country_code
    values['password'] = password
    values['inviter_id'] = inviter_id
    #values['inviter_id'] = '4325572'
    
    #临时解决https的问题
    response = requests.post(url,values,verify=True,proxies=proxies)
    #print(response.text)


if __name__ == '__main__':
    while(True):
        try:
            main()
        except Exception as e:
            print ('str(Exception):\t', str(Exception))
            print ('str(e):\t\t', str(e))
            print ('repr(e):\t', repr(e))
            #print ('e.message:\t', e.message)
            print ('traceback.print_exc():', traceback.print_exc())
            print ('traceback.format_exc():\n%s' % traceback.format_exc())
        print("sleep")
        time.sleep(1)