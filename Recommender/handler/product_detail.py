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

FILE_PATH = (os.path.dirname(os.path.abspath("search.py")) + '/Recommender/data/').replace('\\','/')
DATA_PATH = (os.path.dirname(os.path.dirname(os.path.abspath("search.py"))) + '/RecommendData/').replace('\\','/')

def get_product_info(table,sku):
    #数据初始化
    result = {}
    sql = 'select name,price,img,url,rate,comment_count,description,shop_name,follow_count,sku,avg_price from ' + table + ' where sku=%s;'
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
            temp['nickname'] = nickname
            temp['comment'] = commnet
            useful_comments.append(temp)


    except Exception as err:
        print('product_detail get_comment err:'+str(err))
    finally:
        file.close()

    return useful_comments


@require_http_methods(["POST"])
def get_product_detail(request):
    table = 'cellphone'
    sku = request.POST.get("sku", '')
    result = get_product_info(table,sku)
    score_comments = get_comment(table, sku)
    return render(request, "product-detail.html",{'result':result,'score_comments':score_comments})

