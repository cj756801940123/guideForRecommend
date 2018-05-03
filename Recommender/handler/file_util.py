#!/usr/bin/python
# -*- coding:utf-8 -*-
import os
file_path = (os.path.dirname(os.path.abspath("file_util.py")) + '/Recommender/data/').replace('\\','/')

def del_duplicate(relative_path):
    url_list = []
    file = open(file_path+relative_path, "r", encoding='utf-8')
    for each_line in file:
        url_list.append(each_line.strip("\n"))
    file.close()
    url_list = list(set(url_list))
    file = open(file_path+relative_path, "w", encoding='utf-8')
    for i in url_list:
        file.write(i + '\n')  # 把已经处理了的数据写进文件里面去
    file.close()