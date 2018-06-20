import random

sell_price = 0.00000700
buy_price = 0.00000600



if __name__ == '__main__':
	count = 0
	print(  random.randint(buy_price*100000000,sell_price*100000000) / 100000000 )
	# while(isinstance(sell_price,float)):
	# 	sell_price = sell_price * 10
	# 	print(sell_price)