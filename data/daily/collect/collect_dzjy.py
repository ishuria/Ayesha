# -*- coding: UTF-8 -*-  
import config
import urllib, urllib2
import ssl
import json
import time
import db.db as db
import traceback

page = 0
total_page = 9999

def clearDZJY():
    cursor.execute('truncate table dzjy_history')
    conn.commit()

def updateDZJY(page,cursor):
    global total_page
    content = getDZJYdata(page)
    content = content.replace('pages', '\"pages\"')
    content = content.replace('data', '\"data\"')
    json_content = json.loads(content)
    total_page = int(json_content['pages'])
    data = json_content['data']
    for i in range(len(data)):
        TDATE = data[i]["TDATE"]
        TDATE = TDATE[0:10]
        SECUCODE = data[i]["SECUCODE"]
        SNAME = data[i]["SNAME"]
        PRICE = data[i]["PRICE"]
        TVOL = data[i]["TVOL"]
        TVAL = data[i]["TVAL"]
        BUYERCODE = data[i]["BUYERCODE"]
        BUYERNAME = data[i]["BUYERNAME"]
        SALESCODE = data[i]["SALESCODE"]
        SALESNAME = data[i]["SALESNAME"]
        Stype = data[i]["Stype"]
        Unit = data[i]["Unit"]
        RCHANGE = None if data[i]["RCHANGE"]=='-' else data[i]["RCHANGE"]
        CPRICE = None if data[i]["CPRICE"]=='-' else data[i]["CPRICE"]
        YSSLTAG = None if data[i]["YSSLTAG"]=='-' else data[i]["YSSLTAG"]
        Zyl = None if data[i]["Zyl"]=='-' else data[i]["Zyl"]
        Cjeltszb = None if data[i]["Cjeltszb"]=='-' else data[i]["Cjeltszb"]
        RCHANGE1DC = None if data[i]["RCHANGE1DC"]=='-' else data[i]["RCHANGE1DC"]
        RCHANGE5DC = None if data[i]["RCHANGE5DC"]=='-' else data[i]["RCHANGE5DC"]
        RCHANGE10DC = None if data[i]["RCHANGE10DC"]=='-' else data[i]["RCHANGE10DC"]
        RCHANGE20DC = None if data[i]["RCHANGE20DC"]=='-' else data[i]["RCHANGE20DC"]
        TEXCH = data[i]["TEXCH"]

        cursor.execute(''.join(['insert into dzjy_history ( '
                                    'TDATE, ',
                                    'SECUCODE, ',
                                    'SNAME, ',
                                    'PRICE, ',
                                    'TVOL, ',
                                    'TVAL, ',
                                    'BUYERCODE, ',
                                    'BUYERNAME, ',
                                    'SALESCODE, ',
                                    'SALESNAME, ',
                                    'Stype, ',
                                    'Unit, ',
                                    'RCHANGE, ',
                                    'CPRICE, ',
                                    'YSSLTAG, ',
                                    'Zyl, ',
                                    'Cjeltszb, ',
                                    'RCHANGE1DC, ',
                                    'RCHANGE5DC, ',
                                    'RCHANGE10DC, ',
                                    'RCHANGE20DC, ',
                                    'TEXCH ) values ( ',
                                    '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s ) on duplicate key update ',
                                    'RCHANGE = %s, ',
                                    'CPRICE = %s, ',
                                    'YSSLTAG = %s, ',
                                    'Zyl = %s, ',
                                    'Cjeltszb = %s, ',
                                    'RCHANGE1DC = %s, ',
                                    'RCHANGE5DC = %s, ',
                                    'RCHANGE10DC = %s, ',
                                    'RCHANGE20DC = %s '
                                    ]),[
                                    TDATE,
                                    SECUCODE,
                                    SNAME,
                                    PRICE,
                                    TVOL,
                                    TVAL,
                                    BUYERCODE,
                                    BUYERNAME,
                                    SALESCODE,
                                    SALESNAME,
                                    Stype,
                                    Unit,
                                    RCHANGE,
                                    CPRICE,
                                    YSSLTAG,
                                    Zyl,
                                    Cjeltszb,
                                    RCHANGE1DC,
                                    RCHANGE5DC,
                                    RCHANGE10DC,
                                    RCHANGE20DC,
                                    TEXCH,

                                    RCHANGE,
                                    CPRICE,
                                    YSSLTAG,
                                    Zyl,
                                    Cjeltszb,
                                    RCHANGE1DC,
                                    RCHANGE5DC,
                                    RCHANGE10DC,
                                    RCHANGE20DC])

def getDZJYdata(page):
    url = 'http://dcfm.eastmoney.com/em_mutisvcexpandinterface/api/js/get?type=DZJYXQ&token=70f12f2f4f091e459a279469fe49eca5&cmd=&st={sortType}&sr={sortRule}&p='+str(page)+'&ps={pageSize}&js={pages:(tp),data:(x)}'
    request = urllib2.Request(url)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    response = urllib2.urlopen(request, context=ctx)
    content = response.read()
    return content


def update_daily():
    global page
    page = 0
    conn,cursor = db.db_connect()
    while page <= total_page:
        print('page : ' + str(page) + ' of ' + str(total_page))
        try:
            updateDZJY(page,cursor)
        except:
            print 'traceback.print_exc():'; traceback.print_exc()
            page = page + 1
            continue
        page = page + 1
        time.sleep( 2 )
    conn.commit()
    db.db_close(conn,cursor)


if __name__ == '__main__':
    global page
    page = 0
    conn,cursor = db.db_connect()
    #clearDZJY()
    while page <= total_page:
        print('page : ' + str(page) + ' of ' + str(total_page))
        try:
            updateDZJY(page,cursor)
        except:
            print 'traceback.print_exc():'; traceback.print_exc()
            page = page + 1
            continue
        page = page + 1
        time.sleep( 2 )
    conn.commit()
    db.db_close(conn,cursor)
