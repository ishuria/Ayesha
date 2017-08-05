#coding=utf-8
stock_count_sql = 'SELECT count(1) from stock where stock.`code` = %s'
stock_select_sql =  'SELECT ' +
					'stock.stockType, '+
					'stock.market, '+
					'stock.`name`, '+
					'stock.state, '+
					'stock.currcapital, '+
					'stock.profit_four, '+
					'stock.`code`, '+
					'stock.totalcapital, '+
					'stock.mgjzc, '+
					'stock.pinyin, '+
					'stock.listing_date, '+
					'stock.ct '+
				'FROM '+
					'stock '+
				'WHERE '+
					'stock.`code` = % s '

stock_insert_sql = 'INSERT INTO stock ( '+
						'stock.stockType, '+
						'stock.market, '+
						'stock.`name`, '+
						'stock.state, '+
						'stock.currcapital, '+
						'stock.profit_four, '+
						'stock.`code`, '+
						'stock.totalcapital, '+
						'stock.mgjzc, '+
						'stock.pinyin, '+
						'stock.listing_date, '+
						'stock.ct '+
					') '+
					'VALUES '+
						'( '+
							'% s ,% s ,% s ,% s ,% s ,% s ,% s ,% s ,% s ,% s ,% s ,% s '+
						')'

stock_delete_sql = 'DELETE FROM stock WHERE stock.`code` = %s'

stock_update_sql = 'UPDATE stock '+
					'SET stock.stockType = % s, '+
					 'stock.market = % s, '+
					 'stock.`name` = % s, '+
					 'stock.state = % s, '+
					 'stock.currcapital = % s, '+
					 'stock.profit_four = % s, '+
					 'stock.totalcapital = % s, '+
					 'stock.mgjzc = % s, '+
					 'stock.pinyin = % s, '+
					 'stock.listing_date = % s, '+
					 'stock.ct = % s '+
					'WHERE '+
						'stock.`code` = % s'