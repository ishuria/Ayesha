#coding=utf-8
import stock_list
import stock_history_csv
import stock_history_fq
import stock_increase
import datetime
import sys

if __name__ == '__main__':
	today = datetime.date.today().strftime("%Y-%m-%d")
	if len(sys.argv) == 2 and sys.argv[1] != None:
		today = sys.argv[1]
	#刷新股票列表
	#stock_list.processStockData()
	#抓取每日收盘价、交易量等
	#stock_history_csv.processHistoryData(today,today)
	#抓取复权股价
	#stock_history_fq.processHistoryData(today,today)
	#计算增长率
	stock_increase.processIncrease(today,today)