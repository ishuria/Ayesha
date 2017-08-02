import urllib, urllib2, sys
import ssl


host = 'https://ali-stock.showapi.com'
path = '/stocklist'
method = 'GET'
appcode = 'f86b2760312b41a0b9ef963ceca71b0b'
querys = 'market=sh&page=1'
bodys = {}
url = host + path + '?' + querys

request = urllib2.Request(url)
request.add_header('Authorization', 'APPCODE ' + appcode)
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
response = urllib2.urlopen(request, context=ctx)
content = response.read()
if (content):
    print(content)


with open('result.txt', 'w') as f:
    f.write(content)