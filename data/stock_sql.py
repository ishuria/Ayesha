#coding=utf-8

##################################stock##################################
stock_count_sql = 'SELECT count(1) count from stock where stock.`code` = %s'

stock_select_sql =  ''.join(['SELECT ',
								'stock.stockType, ',
								'stock.market, ',
								'stock.`name`, ',
								'stock.state, ',
								'stock.currcapital, ',
								'stock.profit_four, ',
								'stock.`code`, ',
								'stock.totalcapital, ',
								'stock.mgjzc, ',
								'stock.pinyin, ',
								'stock.listing_date, ',
								'stock.ct ',
							'FROM ',
								'stock ',
							'WHERE ',
								'stock.`code` = %s '])

stock_market_select_sql =  ''.join(['SELECT ',
								'stock.stockType, ',
								'stock.market, ',
								'stock.`name`, ',
								'stock.state, ',
								'stock.currcapital, ',
								'stock.profit_four, ',
								'stock.`code`, ',
								'stock.totalcapital, ',
								'stock.mgjzc, ',
								'stock.pinyin, ',
								'stock.listing_date, ',
								'stock.ct ',
							'FROM ',
								'stock ',
							'WHERE ',
								'stock.market = %s '])

stock_insert_sql = ''.join(['INSERT INTO stock ( ',
								'stock.stockType, ',
								'stock.market, ',
								'stock.`name`, ',
								'stock.state, ',
								'stock.currcapital, ',
								'stock.profit_four, ',
								'stock.`code`, ',
								'stock.totalcapital, ',
								'stock.mgjzc, ',
								'stock.pinyin, ',
								'stock.listing_date, ',
								'stock.ct ',
							') ',
							'VALUES ',
								'( ',
									'%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ',
								')'])

stock_delete_sql = 'DELETE FROM stock WHERE stock.`code` = %s'

stock_update_sql = ''.join(['UPDATE stock ',
							'SET stock.stockType = %s, ',
							 'stock.market = %s, ',
							 'stock.`name` = %s, ',
							 'stock.state = %s, ',
							 'stock.currcapital = %s, ',
							 'stock.profit_four = %s, ',
							 'stock.totalcapital = %s, ',
							 'stock.mgjzc = %s, ',
							 'stock.pinyin = %s, ',
							 'stock.listing_date = %s, ',
							 'stock.ct = %s ',
							'WHERE ',
								'stock.`code` = %s'])
##################################stock##################################end

##################################stock_history##################################
stock_history_count_sql = 'SELECT count(1) count FROM stock_history WHERE stock_history.`code` = %s AND stock_history.date = %s'

stock_history_select_sql =  ''.join(['SELECT ',
								'stock_history.min_price, ',
								'stock_history.market, ',
								'stock_history.trade_num, ',
								'stock_history.trade_money, ',
								'stock_history.close_price, ',
								'stock_history.open_price, ',
								'stock_history.`code`, ',
								'stock_history.max_price, ',
								'stock_history.date '
							'FROM ',
								'stock_history ',
							'WHERE ',
								'stock_history.`code` = %s AND stock_history.date = %s '])

stock_history_insert_sql = ''.join(['INSERT INTO stock_history ( ',
								'stock_history.min_price, ',
								'stock_history.market, ',
								'stock_history.trade_num, ',
								'stock_history.trade_money, ',
								'stock_history.close_price, ',
								'stock_history.open_price, ',
								'stock_history.`code`, ',
								'stock_history.max_price, ',
								'stock_history.date '
							') ',
							'VALUES ',
								'( ',
									'%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ',
								')'])

stock_history_delete_sql = 'DELETE FROM stock_history WHERE stock_history.`code` = %s AND stock_history.date = %s'

stock_history_update_sql = ''.join(['UPDATE stock_history ',
							'SET stock_history.min_price = %s, ',
							 'stock_history.market = %s, ',
							 'stock_history.trade_num = %s, ',
							 'stock_history.trade_money = %s, ',
							 'stock_history.close_price = %s, ',
							 'stock_history.open_price = %s, ',
							 'stock_history.max_price = %s ',
							'WHERE ',
								'stock_history.`code` = %s AND stock_history.date = %s '])
##################################stock_history##################################end