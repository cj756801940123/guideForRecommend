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


@require_http_methods(["POST"])
def get_product_detail(request):
    table = 'cellphone'
    sku = request.POST.get("sku", '')
    result = get_product_info(table,sku)
    return render(request, "product-detail.html",{'result':result})

