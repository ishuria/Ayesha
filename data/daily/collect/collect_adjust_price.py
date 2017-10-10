#coding=utf-8
import urllib2
import ssl
import json
import datetime
import config
import db.db as db
import db.stock as stock
import db.stock_price as stock_price



def collect_adjust_price(begin,end):
    conn,cursor = db.db_connect()

    begin = begin.replace('-','')
    end = end.replace('-','')
    
    for market in config.MARKETS:
        code_list = stock.get_stock_by_market(market,cursor)
        for code in code_list:
            content = None
            if market == 'sh':
                content = request_adjust_price('0'+code)
            else:
                content = request_adjust_price('1'+code)

            if content is None:
                continue
            json_content = json.loads(content)

            closes = json_content['closes']
            times = json_content['times']

            for i in range(0,len(times),1):

                close = closes[i]
                time = times[i]

                if begin <= time and end >= time:
                    c = datetime.datetime.strptime(time,'%Y%m%d')
                    date = c.strftime('%Y-%m-%d')

                    print('refreshing stock adjust price ' + code + ' ' + date)
                    params = [close,code,date]
                    stock_price.refresh_stock_adjust_price(params,cursor)

            conn.commit()
    conn.commit()
    db.db_close(conn,cursor)


def request_adjust_price(code):
    try:
        url = config.FQ_PRICE_HOST + '/' + code + '.json'
        request = urllib2.Request(url)
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        response = urllib2.urlopen(request, context=ctx)
        content = response.read()
        return content
    except:
        return None


if __name__ == '__main__':
    collect_adjust_price('2017-08-14','2017-08-14')