#coding=utf-8
import MySQLdb as mdb



def refresh_stock_increase(params,cursor):
    """insert or update stock increase.

    Args:
        params: data.
        cursor: data base cursor.

    Returns:
        None

    Raises:
        None
    """
    sql = ('INSERT INTO stock_increase ( '
            'stock_increase.date, '
            'stock_increase.`code`, '
            'stock_increase.inc_day, '
            'stock_increase.inc_30, '
            'stock_increase.inc_90, '
            'stock_increase.inc_180, '
            'stock_increase.inc_360, '
            'stock_increase.fit_inc_30_1, '
            'stock_increase.fit_inc_30_2, '
            'stock_increase.fit_inc_90_1, '
            'stock_increase.fit_inc_90_2, '
            'stock_increase.fit_inc_180_1, '
            'stock_increase.fit_inc_180_2, '
            'stock_increase.fit_inc_360_1, '
            'stock_increase.fit_inc_360_2 '
        ') VALUES ( '
                '%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s,%s ,%s,%s ,%s,%s ,%s '
            ') ON DUPLICATE KEY UPDATE stock_increase.inc_day = %s, '
            'stock_increase.inc_30 = %s, '
            'stock_increase.inc_90 = %s, '
            'stock_increase.inc_180 = %s, '
            'stock_increase.inc_360 = %s, '
            'stock_increase.fit_inc_30_1 = %s, '
            'stock_increase.fit_inc_30_2 = %s, '
            'stock_increase.fit_inc_90_1 = %s, '
            'stock_increase.fit_inc_90_2 = %s, '
            'stock_increase.fit_inc_180_1 = %s, '
            'stock_increase.fit_inc_180_2 = %s, '
            'stock_increase.fit_inc_360_1 = %s, '
            'stock_increase.fit_inc_360_2 = %s ' )
    cursor.execute(sql , params)



