# -*- coding: utf-8 -*-
coding='UTF-8'
import re

def rr(filename):
    #找到有HH:mm:ss格式时间的行（qq中每条信息前都有发言人和时间）对此处修改可寻找特殊的发言人信息
    pattern = re.compile('.*? \d{1,2}:\d{1,2}:\d{1,2}',re.S)
    fr = open(filename,'r',encoding=coding)
    #读取旧的聊天记录文件
    lines = fr.readlines()
    num = 1
    #新文件保存位置，名字与旧文件一致
    newFilename = 'D:/git/Ayesha/chat/train' + filename+'1'
    #创建文件
    fn = open(newFilename, 'w')
    fn.close()
    for line in lines:
        search = pattern.search(line)
        if search:
            #对找到的发言人所在一行内容前加星号和编号，换号符
            newLine ='\n'+'************'+ str(num) + ':' +line +'\n'
            num = num + 1
        else:
            #普通行只在内容后添加换行符
            newLine=line + '\n'
        #逐行写入聊天信息
        fw = open(newFilename, 'ab+')
        fw.write(bytearray(newLine, 'utf-8'))
        fw.flush()
        fw.close()
    fr.close()

#旧文件名。默认位置和该py文件在一个文件夹下
filename =u'111697557.txt'
rr(filename)