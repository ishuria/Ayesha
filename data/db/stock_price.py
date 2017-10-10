#coding=utf-8
import datetime
import MySQLdb as mdb

def refresh_stock_price(params,cursor):
    """insert or update stock price.

    Args:
        params: data.
        cursor: data base cursor.

    Returns:
        None

    Raises:
        None
    """
    sql = ('INSERT INTO stock_history ( '
            'stock_history.min_price, '
            'stock_history.market, '
            'stock_history.trade_num, '
            'stock_history.trade_money, '
            'stock_history.close_price, '
            'stock_history.open_price, '
            'stock_history.`code`, '
            'stock_history.max_price, '
            'stock_history.date, '
            'stock_history.last_close_price, '
            'stock_history.increase, '
            'stock_history.increase_rate, '
            'stock_history.turnover_rate, '
            'stock_history.total_value, '
            'stock_history.circulation_value '
        ') VALUES ( %s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s,%s ,%s,%s ,%s,%s ,%s '
            ') ON DUPLICATE KEY UPDATE min_price = %s, '
            'stock_history.market = %s, '
            'stock_history.trade_num = %s, '
            'stock_history.trade_money = %s, '
            'stock_history.close_price = %s, '
            'stock_history.open_price = %s, '
            'stock_history.max_price = %s, '
            'stock_history.last_close_price = %s, '
            'stock_history.increase = %s, '
            'stock_history.increase_rate = %s, '
            'stock_history.turnover_rate = %s, '
            'stock_history.total_value = %s, '
            'stock_history.circulation_value = %s ' )
    cursor.execute(sql , params)


def refresh_stock_adjust_price(params,cursor):
    """insert or update stock adjust price.

    Args:
        params: data.
        cursor: data base cursor.

    Returns:
        None

    Raises:
        None
    """
    sql = ( 'UPDATE stock_history '
            'SET stock_history.fq_close_price = %s '
            'WHERE stock_history.`code` = %s AND stock_history.date = %s ')
    cursor.execute(sql , params)



def get_stock_increase_calculation_set(begin,end,code,cursor):
    """query table stock_history

    Args:
        begin: start date.
        end: end date.
        code: stock code.
        cursordata base cursor.

    Returns:
        A list of stock price

    Raises:
        None
    """
    stock_history_list = []

    enddate = datetime.datetime(int(end[0:4]),int(end[5:7]),int(end[8:10]))
    begindate = datetime.datetime(int(begin[0:4]),int(begin[5:7]),int(begin[8:10]))
    diff = (enddate-begindate).days

    sql = ('SELECT * FROM ( '
            'SELECT '
                'stock_history.min_price, '
                'stock_history.market, '
                'stock_history.trade_num, '
                'stock_history.trade_money, '
                'stock_history.close_price, '
                'stock_history.open_price, '
                'stock_history.`code`, '
                'stock_history.max_price, '
                'stock_history.date, '
                'stock_history.last_close_price, '
                'stock_history.increase, '
                'stock_history.increase_rate, '
                'stock_history.turnover_rate, '
                'stock_history.total_value, '
                'stock_history.circulation_value, '
                'stock_history.fq_close_price '
            'FROM stock_history '
            'WHERE stock_history.`code` = %s '
            'AND stock_history.fq_close_price IS NOT NULL '
            'AND date <= %s '
            'ORDER BY date DESC '
            'LIMIT 0, %s '
            ') t ORDER BY date ASC ')
    cursor.execute(sql, [code,end,diff + 380])

    results = cursor.fetchall()
    for result in results:
        stock_history_list.append(result)

    return stock_history_list


def get_stock_future_calculation_set(begin,end,code,cursor):
    """query table stock_history

    Args:
        begin: start date.
        end: end date.
        code: stock code.
        cursordata base cursor.

    Returns:
        A list of stock price

    Raises:
        None
    """
    stock_future_list = []

    enddate = datetime.datetime(int(end[0:4]),int(end[5:7]),int(end[8:10]))
    begindate = datetime.datetime(int(begin[0:4]),int(begin[5:7]),int(begin[8:10]))
    diff = (enddate-begindate).days

    sql = ('SELECT * FROM ( '
            'SELECT '
                'stock_history.min_price, '
                'stock_history.market, '
                'stock_history.trade_num, '
                'stock_history.trade_money, '
                'stock_history.close_price, '
                'stock_history.open_price, '
                'stock_history.`code`, '
                'stock_history.max_price, '
                'stock_history.date, '
                'stock_history.last_close_price, '
                'stock_history.increase, '
                'stock_history.increase_rate, '
                'stock_history.turnover_rate, '
                'stock_history.total_value, '
                'stock_history.circulation_value, '
                'stock_history.fq_close_price '
            'FROM stock_history '
            'WHERE stock_history.`code` = %s '
            'AND stock_history.fq_close_price IS NOT NULL '
            'AND date >= %s '
            'ORDER BY date ASC '
            'LIMIT 0, %s '
            ') t ORDER BY date DESC ')
    cursor.execute(sql, [code,begin,diff + 380])

    results = cursor.fetchall()
    for result in results:
        stock_future_list.append(result)

    return stock_future_list
