# -*- coding: UTF-8 -*-  
import subprocess


p = subprocess.Popen('python stock_learn_2.py', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
for line in p.stdout.readlines():
    print line,
retval = p.wait()



p = subprocess.Popen('python stock_learn_2.py', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
for line in p.stdout.readlines():
    print line,
retval = p.wait()



p = subprocess.Popen('python stock_learn_2.py', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
for line in p.stdout.readlines():
    print line,
retval = p.wait()



p = subprocess.Popen('python stock_learn_2.py', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
for line in p.stdout.readlines():
    print line,
retval = p.wait()