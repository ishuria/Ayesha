#coding=utf-8
import collect_price
import collect_adjust_price
import collect_increase
import collect_train_data
import collect_dzjy
import datetime
import sys

if __name__ == '__main__':
	today = datetime.date.today().strftime("%Y-%m-%d")
	begin_date = datetime.date.today().strftime("%Y-%m-%d")
	end_date = datetime.date.today().strftime("%Y-%m-%d")
	if len(sys.argv) == 1:
		#抓取每日收盘价、交易量等
		collect_price.collect_price(today,today)
		#抓取复权股价
		collect_adjust_price.collect_adjust_price(today,today)
		#计算增长率
		collect_increase.collect_increase(today,today)
		#生成训练数据
		collect_train_data.collect_train_data(today,today)
		#抓取大宗交易数据
		collect_dzjy.update_daily()
	if len(sys.argv) == 2 and sys.argv[1] != None:
		today = sys.argv[1]
		#抓取每日收盘价、交易量等
		collect_price.collect_price(today,today)
		#抓取复权股价
		collect_adjust_price.collect_adjust_price(today,today)
		#计算增长率
		collect_increase.collect_increase(today,today)
		#生成训练数据
		collect_train_data.collect_train_data(today,today)
		#抓取大宗交易数据
		collect_dzjy.update_daily()
	if len(sys.argv) == 3 and sys.argv[1] != None and sys.argv[2] != None:
		begin_date = sys.argv[1]
		end_date = sys.argv[2]
		#抓取每日收盘价、交易量等
		collect_price.collect_price(begin_date,end_date)
		#抓取复权股价
		collect_adjust_price.collect_adjust_price(begin_date,end_date)
		#计算增长率
		collect_increase.collect_increase(begin_date,end_date)
		#生成训练数据
		collect_train_data.collect_train_data(today,today)
		#抓取大宗交易数据
		collect_dzjy.update_daily()
