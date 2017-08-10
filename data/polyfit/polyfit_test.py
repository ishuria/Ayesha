#coding=utf-8
import numpy as np


def test():
	X=[ 1 ,2  ,3 ,4 ,5 ,6]
	Y=[ 2.5 ,3.51 ,4.45 ,5.52 ,6.47 ,7.51]
	z1 = np.polyfit(X, Y, 1)  #一次多项式拟合，相当于线性拟合
	p1 = np.poly1d(z1)
	print z1  #[ 1.          1.49333333]
	print z1[0]
	print z1[1]
	print p1  # 1 x + 1.493


if __name__ == '__main__':
	test()