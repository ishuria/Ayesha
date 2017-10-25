#coding=utf-8
import os
import re

def clear_old_model_file():
    pattern = re.compile('"(.*)"')
    model_file_path = '/home/ayesha/data/models/'
    sub_model_file_dirs =  os.listdir(model_file_path)
    for stock_dir in sub_model_file_dirs:
        checkpoint_file = os.path.join('%s%s%s' % (model_file_path,stock_dir,'/30/checkpoint'))
        try:
            with open(checkpoint_file, 'r') as f:
                for line in f:
                    last_model_file_path = pattern.findall(line)[0]

                    for x in os.listdir(model_file_path+stock_dir+'/30/'):
                        path_now = os.path.join(model_file_path+stock_dir+'/30/', x)
                        if os.path.isfile(path_now) and (path_now.find(last_model_file_path)>=0 or path_now.find('checkpoint') >= 0):
                            pass
                        else:
                            os.remove(path_now)
        except IOError:  
            print "there is an erroe when open and load %s" %checkpoint_file  


if __name__ == '__main__':
    clear_old_model_file()