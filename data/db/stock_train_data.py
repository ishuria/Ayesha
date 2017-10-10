#coding=utf-8
import MySQLdb as mdb








def refresh_stock_train_data(params,cursor):
    """insert or update stock train_data.

    Args:
        params: data.
        cursor: data base cursor.

    Returns:
        None

    Raises:
        None
    """
    sql = ('INSERT INTO stock_train_data ( '
            'stock_train_data.date, '
            'stock_train_data.`code`, '
            'stock_train_data.inc_30, '
            'stock_train_data.inc_90, '
            'stock_train_data.inc_180, '
            'stock_train_data.inc_360, '
            'stock_train_data.turn_30, '
            'stock_train_data.turn_90, '
            'stock_train_data.turn_180, '
            'stock_train_data.turn_360, '
            'stock_train_data.trade_money_30, '
            'stock_train_data.trade_money_90, '
            'stock_train_data.trade_money_180, '
            'stock_train_data.trade_money_360, '
            'stock_train_data.trade_num_30, '
            'stock_train_data.trade_num_90, '
            'stock_train_data.trade_num_180, '
            'stock_train_data.trade_num_360, '
            'stock_train_data.future_inc_30, '
            'stock_train_data.future_inc_90, '
            'stock_train_data.future_inc_180, '
            'stock_train_data.future_inc_360, '
            'stock_train_data.future_price_30, '
            'stock_train_data.future_price_90, '
            'stock_train_data.future_price_180, '
            'stock_train_data.future_price_360 '
        ') VALUES ( '
                '%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s,%s ,%s,%s ,%s,%s ,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s '
            ') ON DUPLICATE KEY UPDATE stock_train_data.inc_30 = %s, '
            'stock_train_data.inc_90 = %s, '
            'stock_train_data.inc_180 = %s, '
            'stock_train_data.inc_360 = %s, '
            'stock_train_data.turn_30 = %s, '
            'stock_train_data.turn_90 = %s, '
            'stock_train_data.turn_180 = %s, '
            'stock_train_data.turn_360 = %s, '
            'stock_train_data.trade_money_30 = %s, '
            'stock_train_data.trade_money_90 = %s, '
            'stock_train_data.trade_money_180 = %s, '
            'stock_train_data.trade_money_360 = %s, '
            'stock_train_data.trade_num_30 = %s, '
            'stock_train_data.trade_num_90 = %s, '
            'stock_train_data.trade_num_180 = %s, '
            'stock_train_data.trade_num_360 = %s, '
            'stock_train_data.future_inc_30 = %s, '
            'stock_train_data.future_inc_90 = %s, '
            'stock_train_data.future_inc_180 = %s, '
            'stock_train_data.future_inc_360 = %s, '
            'stock_train_data.future_price_30 = %s, '
            'stock_train_data.future_price_90 = %s, '
            'stock_train_data.future_price_180 = %s, '
            'stock_train_data.future_price_360 = %s ' )
    cursor.execute(sql , params)


def refresh_future_price(params,cursor):
    cursor.execute('update stock_train_data set future_price_30 = %s where `code` = %s and date = %s',params)
