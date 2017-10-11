#coding=utf-8
import MySQLdb as mdb


def refresh_stock_est_data(params,cursor):
    """insert or update stock train_data.

    Args:
        params: data.
        cursor: data base cursor.

    Returns:
        None

    Raises:
        None
    """
    sql = ('INSERT INTO stock_est_data ( '
        '   `code`, date, est_price_30, future_price_30 '
        ' ) VALUES ( '
        '       %s ,%s ,%s ,%s '
        '   ) ON DUPLICATE KEY UPDATE est_price_30 = %s, '
        '   future_price_30 = %s ')
    cursor.execute(sql , params)
