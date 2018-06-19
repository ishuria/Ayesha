# HttpClient.py is written by [xqin]: https://github.com/xqin/SmartQQ-for-Raspberry-Pi
import http.cookiejar, urllib, urllib.request

class HttpClient:
    __cookie = http.cookiejar.CookieJar()
    __req = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(__cookie))
    __req.addheaders = [
        ('Accept', 'application/javascript, */*;q=0.8'),
        ('User-Agent', 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)')
    ]
    urllib.request.install_opener(__req)

    def Get(self, url, refer=None):
        try:
            req = urllib.request.Request(url)
            if not (refer is None):
                req.add_header('Referer', refer)
            return urllib.request.urlopen(req).read()
        except urllib.request.HTTPError as e:
            return e.read()

    def Post(self, url, data, refer=None):
        print(url)
        print(data)
        try:
            req = urllib.request.Request(url, urllib.parse.urlencode(data).encode("utf-8"))
            if not (refer is None):
                req.add_header('Referer', refer)
            return urllib.request.urlopen(req).read()
        except urllib.request.HTTPError as e:
            return e.read()

    def Download(self, url, file):
        output = open(file, 'wb')
        output.write(urllib.request.urlopen(url).read())
        output.close()

#  def urlencode(self, data):
#    return urllib.quote(data)

    def getCookie(self, key):
        for c in self.__cookie:
            if c.name == key:
                return c.value
        return ''

    def setCookie(self, key, val, domain):
        ck = cookielib.Cookie(version=0, name=key, value=val, port=None, port_specified=False, domain=domain, domain_specified=False, domain_initial_dot=False, path='/', path_specified=True, secure=False, expires=None, discard=True, comment=None, comment_url=None, rest={'HttpOnly': None}, rfc2109=False)
        self.__cookie.set_cookie(ck)
#self.__cookie.clear() clean cookie
# vim : tabstop=2 shiftwidth=2 softtabstop=2 expandtab