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


def handle_sql_results(table,keywords,price1,price2):
    #获取weight表中的参数，便于后面排序
    sql = 'select rate,follow,comment,sentiment,brand_hot,sum,comment_score,hot_score from weight'
    result = database_util.search_sql(sql, None)
    if result[0] != -1:
        i = list(result[1])[0]
        sum = i[5]
        w_rate = float(i[0]) / sum
        w_follow = float(i[1]) / sum
        w_comment = float(i[2]) / sum
        w_sentiment = float(i[3]) / sum
        w_brand = float(i[4]) / sum
        comment_score = float(i[6])
        hot_score = float(i[7])

    # 进行sql查询并处理查询结果
    all_list = []
    sql = 'select name,price,img,url,rate,comment,description,shop_name,follow,sku,sentiment,brand_hot from '
    if keywords == '':
        item_sql = sql + table + ' where price>=%s and price<=%s;'
        sql_result = database_util.search_sql(item_sql, [int(price1), int(price2)])
    else:
        item_sql = sql+table+' where match(description) against(%s in natural language mode) and price>=%s and price<=%s;'
        sql_result = database_util.search_sql(item_sql, [keywords,int(price1), int(price2)])
    if sql_result[0]!=-1:
        temp = list(sql_result[1])
        for t in temp:
            j = list(t)
            score = round((float(j[4]) * w_rate + float(j[8])*w_follow/hot_score + float(j[5]) * w_comment/comment_score + float(j[10]) * w_sentiment + float(j[11])* w_brand/hot_score), 2)
            j.append(score)
            all_list.append(j)

    # 排序之后输出结束
    all_list.sort(key=itemgetter(10), reverse=True)
    item1 = []
    item2 = []
    for i in range(18):
        if (i < len(all_list)):
            temp = {}
            temp["name"] = all_list[i][0]
            temp["price"] = str(all_list[i][1])
            temp["img"] = all_list[i][2]
            temp["address"] = all_list[i][3]
            temp["rate"] = str(round(all_list[i][4] * 100, 2)) + '%'
            if all_list[i][5] > 10000:
                all_list[i][5] = str(float(all_list[i][5]) / 10000) + '万+'
            if all_list[i][8] > 10000:
                all_list[i][8] = str(float(all_list[i][8]) / 10000) + '万'
            temp["comment"] = all_list[i][5]
            temp["description"] = all_list[i][6]
            temp["shop"] = all_list[i][7]
            temp["follow"] = all_list[i][8]
            temp["sku"] = all_list[i][9]
            if i < 9:
                item1.append(temp)
            else:
                item2.append(temp)

    #获取热门品牌排名
    brands = []
    brand_sql = 'select shop_name,brand ,follow from ' + table + ' group by brand order by follow desc limit 12;'
    sql_result = database_util.search_sql(brand_sql,None)
    if sql_result[0] != -1:
        sql_result = list(sql_result[1])
        for j in sql_result:
            i = list(j)
            temp = {}
            if i[2] > 10000:
                i[2] = str(float(i[2]) / 10000) + '万'
            temp["brand"] = i[1]
            temp["shop"] = i[0]
            temp["follow"] = i[2]
            temp["num"] = i
            brands.append(temp)

    results = {}
    results['data1'] = item1
    results['data2'] = item2
    results['brands'] = brands
    return results

def get_products(message):
    keywords = message['keywords']
    price1 = message['price1']
    price2 = message['price2']
    table = 'cellphone'
    result = handle_sql_results(table, keywords,price1,price2)
    return result

@require_http_methods(["POST"])
def search_product(request):
    message = {}
    message['kind'] = request.POST.get("kind", '')
    message['keywords'] = request.POST.get("keywords", '')
    message['price1'] = request.POST.get("price1", '')
    message['price2'] = request.POST.get("price2", '')
    if  message['price1'] =='':
        message['price1'] = 0
    if  message['price2'] =='':
        message['price2'] = 5000
    results = get_products(message)
    return render(request, "product.html",{'message':message,'brands':results['brands'],'data1':results['data1'],'data2':results['data2']})
