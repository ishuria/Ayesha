#coding=utf-8
import stock_list
import stock_history_csv
import stock_history_fq
import stock_increase
import stock_train_data
import collect_dzjy
import datetime
import sys

if __name__ == '__main__':
	today = datetime.date.today().strftime("%Y-%m-%d")
	begin_date = datetime.date.today().strftime("%Y-%m-%d")
	end_date = datetime.date.today().strftime("%Y-%m-%d")
	if len(sys.argv) == 1:
		#刷新股票列表
		#stock_list.processStockData()
		#抓取每日收盘价、交易量等
		stock_history_csv.processHistoryData(today,today)
		#抓取复权股价
		stock_history_fq.processHistoryData(today,today)
		#计算增长率
		stock_increase.processIncrease(today,today)
		#生成训练数据
		stock_train_data.processIncrease(today,today)
		#抓取大宗交易数据
		collect_dzjy.update_daily()
	if len(sys.argv) == 2 and sys.argv[1] != None:
		today = sys.argv[1]
		#刷新股票列表
		#stock_list.processStockData()
		#抓取每日收盘价、交易量等
		stock_history_csv.processHistoryData(today,today)
		#抓取复权股价
		stock_history_fq.processHistoryData(today,today)
		#计算增长率
		stock_increase.processIncrease(today,today)
		#生成训练数据
		stock_train_data.processIncrease(today,today)
		#抓取大宗交易数据
		collect_dzjy.update_daily()
	if len(sys.argv) == 3 and sys.argv[1] != None and sys.argv[2] != None:
		begin_date = sys.argv[1]
		end_date = sys.argv[2]
		#刷新股票列表
		#stock_list.processStockData()
		#抓取每日收盘价、交易量等
		stock_history_csv.processHistoryData(begin_date,end_date)
		#抓取复权股价
		stock_history_fq.processHistoryData(begin_date,end_date)
		#计算增长率
		stock_increase.processIncrease(begin_date,end_date)
		#生成训练数据
		stock_train_data.processIncrease(begin_date,end_date)
		#抓取大宗交易数据
		collect_dzjy.update_daily()
