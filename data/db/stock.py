#coding=utf-8
import MySQLdb as mdb

def get_stock_by_market(market,cursor):
    """Get a list of stock code from market code.

    Args:
        market: market code.
        cursor: data base cursor.

    Returns:
        A list of stock code.

    Raises:
        None
    """
    stock_list = []
    sql = ('SELECT '
            'stock.stockType, '
            'stock.market, '
            'stock.`name`, '
            'stock.state, '
            'stock.currcapital, '
            'stock.profit_four, '
            'stock.`code`, '
            'stock.totalcapital, '
            'stock.mgjzc, '
            'stock.pinyin, '
            'stock.listing_date, '
            'stock.ct '
        'FROM '
            'stock '
        'WHERE '
            'stock.market = %s ')
    cursor.execute(sql , [market])
    results = cursor.fetchall()
    for result in results:
        stock_list.append(result[6])
    return stock_list


def get_train_data(code,date,data_size,cursor):
    """Get training data.

    Args:
        code: stock code.
        date: training date.
        data_size: training data size.
        cursor: data base cursor.
        
    Returns:
        A list of training data.

    Raises:
        None
    """
    sql = ('SELECT * FROM ( '
            'SELECT '
            '   t.trade_num, '
            '   t.fq_close_price, '
            '   t.trade_money,  '
            '   t.circulation_value,  '
            '   t.trade_money / t.circulation_value * 100 trade_rate, '
            '   t.turnover_rate, '
            '   ifnull( sum(t2.tvol * t2.PRICE * 10000) / t.circulation_value * 100, 0 ) dzjy_rate, '
            '   d.future_price_30, '
            '   t.date '
            '   FROM stock_history t '
            '   LEFT JOIN dzjy_history t2 ON t.date = t2.tdate AND t.`code` = t2.secucode '
            '   LEFT JOIN stock_train_data d ON d.`code` = t.`code` AND d.date = t.date '
            '   WHERE '
            '       t.date <= %s  '
            '   AND t.`code` = %s  '
            '   AND t.date IS NOT NULL '
            '   AND t.trade_num IS NOT NULL '
            '   AND t.trade_money IS NOT NULL '
            '   AND t.fq_close_price IS NOT NULL '
            '   AND t.turnover_rate IS NOT NULL '
            '   AND d.future_price_30 IS NOT NULL '
            '   AND t.close_price IS NOT NULL '
            '   GROUP BY '
            '   t.date, '
            '   t.close_price, '
            '   t.trade_num, '
            '   t.trade_money, '
            '   t.fq_close_price, '
            '   t.turnover_rate, '
            '   d.future_price_30 '
            '   ORDER BY t.date DESC '
            '   LIMIT 0, '+ str(data_size) +' ) tt '
            '   ORDER BY date ASC')
    cursor.execute(sql , [date,code])
    return cursor.fetchall()


def get_estimation_data(code,date,data_size,cursor):
    """Get estimation data.

    Args:
        code: stock code.
        date: training date.
        data_size: training data size.
        cursor: data base cursor.
        
    Returns:
        A list of training data.

    Raises:
        None
    """
    sql = ('SELECT * FROM ( '
            'SELECT '
            '   t.trade_num, '
            '   t.fq_close_price, '
            '   t.trade_money,  '
            '   t.circulation_value,  '
            '   t.trade_money / t.circulation_value * 100 trade_rate, '
            '   t.turnover_rate, '
            '   ifnull( sum(t2.tvol * t2.PRICE * 10000) / t.circulation_value * 100, 0 ) dzjy_rate, '
            '   d.future_price_30, '
            '   t.date '
            '   FROM stock_history t '
            '   LEFT JOIN dzjy_history t2 ON t.date = t2.tdate AND t.`code` = t2.secucode '
            '   LEFT JOIN stock_train_data d ON d.`code` = t.`code` AND d.date = t.date '
            '   WHERE '
            '       t.date <= %s  '
            '   AND t.`code` = %s  '
            '   AND t.date IS NOT NULL '
            '   AND t.trade_num IS NOT NULL '
            '   AND t.trade_money IS NOT NULL '
            '   AND t.fq_close_price IS NOT NULL '
            '   AND t.turnover_rate IS NOT NULL '
            '   AND t.close_price IS NOT NULL '
            '   GROUP BY '
            '   t.date, '
            '   t.close_price, '
            '   t.trade_num, '
            '   t.trade_money, '
            '   t.fq_close_price, '
            '   t.turnover_rate, '
            '   d.future_price_30 '
            '   ORDER BY t.date DESC '
            '   LIMIT 0, '+ str(data_size) +' ) tt '
            '   ORDER BY date ASC')
    cursor.execute(sql , [date,code])
    return cursor.fetchall()