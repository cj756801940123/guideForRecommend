#!/usr/bin/python
# -*- coding:utf-8 -*-
import os
from operator import itemgetter
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.shortcuts import render
from Recommender.handler import database_util
from Recommender.handler import file_util
from Recommender.handler import similarity_util
import jieba
import json

FILE_PATH = (os.path.dirname(os.path.dirname(os.path.abspath("search.py"))) + '/Recommendation/data/').replace('\\','/')
DATA_PATH = (os.path.dirname(os.path.dirname(os.path.abspath("search.py"))) + '/RecommendData/').replace('\\','/')


def get_product_info(table,sku):
    #数据初始化
    result = {}
    sql = 'select name,price,img,url,rate,comment,description,shop_name,follow,sku,avg_price,sentiment from ' + table + ' where sku=%s;'
    data = [sku]
    sql_result = database_util.search_sql(sql, data)
    if sql_result[0]!=-1:
        temp = list(sql_result[1][0])
        result["name"] = temp[0]
        result["price"] = temp[1]
        result["img"] = temp[2]
        result["address"] = temp[3]
        result["rate"] = str( round(temp[4]*100,2))+'%'
        if temp[5] > 10000:
           temp[5] = str(float(temp[5]) / 10000) + '万+'
        if temp[8] > 10000:
            temp[8] = str(float(temp[8]) / 10000) + '万'
        result["comment"] = temp[5]
        result["description"] = temp[6]
        result["shop"] = temp[7]
        result["follow"] = temp[8]
        result["sku"] = temp[9]
        result["avg_price"] = temp[10]
        result["sentiment"] = int(temp[11])
    return result

def get_comment(table,sku):
    useful_file = DATA_PATH+table+'/score_comments/'+sku+'.txt'
    try:
        file = open(useful_file, "r", encoding='utf-8')
        useful_comments = []
        for each_line in file:
            temp = {}
            index = each_line.index(' ')
            score = each_line[0:index]
            star = each_line[index+1:index+2]
            c_index = each_line.find(' comment:')
            nickname = each_line[index+12:c_index]
            commnet = each_line[c_index+9:].strip('\n')
            temp['score'] = score
            temp['star'] = star
            temp['nickname'] = '    '+nickname
            temp['comment'] = commnet
            useful_comments.append(temp)
    except Exception as err:
        print('product_detail get_comment err:'+str(err))
    finally:
        file.close()
    return len(useful_comments),useful_comments

def get_unreal_comment(table,sku):
    unreal_file = DATA_PATH+table+'/unreal_comments/'+sku+'.txt'
    if not os.path.exists(unreal_file):
        return 0,[]
    try:
        file = open(unreal_file, "r", encoding='utf-8')
        unreal_comments = []
        for each_line in file:
            temp = {}
            star = each_line[0]
            c_index = each_line.find(' comment:')
            nickname = each_line[13:c_index]
            commnet = each_line[c_index+9:].strip('\n')
            temp['star'] = star
            temp['nickname'] = nickname
            temp['comment'] = commnet
            unreal_comments.append(temp)
    except Exception as err:
        print('product_detail get_unreal_comment err:'+str(err))
    finally:
        file.close()
    return len(unreal_comments),unreal_comments

def get_attribute(table):
    try:
        fin = open(FILE_PATH+'procedure_files/'+table+'_attributes.txt', 'r', encoding='utf-8')  # 以读的方式打开文件
        attribute_words = []
        for eachLine in fin:
            word = eachLine.strip()
            words = word.split(',')
            attribute_words.append(words[0])
    except Exception as err:
        print('product_detail get_attribute err:'+str(err))
    finally:
        fin.close()
    return attribute_words


@require_http_methods(["POST"])
def get_product_detail(request):
    table = 'cellphone'
    sku = request.POST.get("sku", '')
    print(sku)
    result = get_product_info(table,sku)
    temp = get_comment(table, sku)
    useful = temp[0]
    score_comments = temp[1]
    temp = get_unreal_comment(table, sku)
    unreal_comments = temp[1]
    unreal = temp[0]
    unreal_rate = str(round(unreal*1.0/(useful+unreal)*100.0,2))+'%'
    attributes = get_attribute(table)
    return render(request, "product-detail.html",{'result':result,'score_comments':score_comments,
                              'unreal_comments':unreal_comments,'attributes':attributes,'unreal_rate':unreal_rate})

