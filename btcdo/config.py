import configparser
import requests

cp=configparser.ConfigParser()
cp.read("./config.ini")

api_key = cp.get('account','api_key')
secret_key = cp.get('account','secret_key')
api_url = cp.get('app','api_url')
symbol = cp.get('app','symbol')
amount = cp.get('app','amount')


headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
session = requests.session()