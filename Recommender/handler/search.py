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

#获取应该去哪些数据库表中查询
def get_tables(keyword):
    tables = ['cellphone']
    print(keyword)
    return tables,keyword

def get_other_tables(tables):
    kinds = ['product_lipstick','product_eye','product_perfume', 'product_baseMakeup','product_other_perfume']
    for i in tables:
        kinds.remove(i)
    return kinds

def handle_sql_results(tables,keywords,price1,price2,page_no):
    #数据初始化
    results = {}
    message = {}
    results['data1'] = {}
    results['data2'] = {}
    results['brands'] = {}
    item_sql = []
    brand_sql = []
    print(price1,price2)
    for i in tables:
        if keywords == '':
            sql1 = 'select name,price,img,url,rate,comment_count,description,shop_name,follow_count,sku from ' + i + ' where price>=%s and price<=%s;'
            data = [int(price1), int(price2)]
        else:
            sql1 = 'select name,price,img,url,rate,comment_count,description,shop_name,follow_count,sku from '+i+' ' \
       'where match(description) against(%s in natural language mode) and price>=%s and price<=%s;'
            data = [keywords, int(price1), int(price2)]
        sql2 = 'select shop_name,brand ,follow_count from '+i+' group by brand order by follow_count desc limit 10;'
        item_sql.append(sql1)
        brand_sql.append(sql2)

    # 进行sql查询并处理查询结果
    all_list = []
    for i in item_sql:
        temp = database_util.search_sql(i, data)
        code = int(temp[0])
        if code==-1:
            message['error_code'] = 1
            message['msg'] = temp[1]
            message['page_count'] = 0
            continue
        temp = list(temp[1])
        if len(temp)==0:
            continue
        for j in temp:
            item = list(j)
            all_list.append(item)

    all_brands = []
    for i in brand_sql:
        temp = database_util.search_sql(i,None)
        code = int(temp[0])
        if code==-1:
            continue
        temp = list(temp[1])
        if len(temp)==0:
            continue
        for j in temp:
            item = list(j)
            all_brands.append(item)

    if len(all_list) ==0:
        message['error_code'] = 1
        message['msg'] = '搜索不出对应的产品!'
        message['page_count'] = 0
        results['message'] = message
        return results

    #排序之后输出结束
    start = (page_no-1)*18
    all_list.sort(key=itemgetter(5, 8), reverse=True)
    all_brands.sort(key=itemgetter(2), reverse=True)
    item1 = []
    item2 = []
    for i in range(start,start+18):
        if(i<len(all_list)):
            temp = {}
            temp["name"] = all_list[i][0]
            temp["price"] = str(all_list[i][1])
            temp["img"] = all_list[i][2]
            temp["address"] = all_list[i][3]
            temp["rate"] = str( round(all_list[i][4]*100,2))+'%'
            if all_list[i][5] > 10000:
                all_list[i][5] = str(float(all_list[i][5]) / 10000) + '万+'
            if all_list[i][8] > 10000:
                all_list[i][8] = str(float(all_list[i][8]) / 10000) + '万'
            temp["comment"] = all_list[i][5]
            temp["description"] = all_list[i][6]
            temp["shop"] = all_list[i][7]
            temp["follow"] = all_list[i][8]
            temp["sku"] = all_list[i][9]
            if i<start+9:
                item1.append(temp)
            else:
                item2.append(temp)

    brands = []
    for i in range(0,10):
            temp = {}
            if all_brands[i][2] > 10000:
                all_brands[i][2] = str(float(all_brands[i][2]) / 10000) + '万'
            temp["brand"] = all_brands[i][1]
            temp["shop"] = all_brands[i][0]
            temp["follow"] = all_brands[i][2]
            temp["num"] = i
            brands.append(temp)

    message['error_code'] = 0
    message['msg'] = 'success'
    results['data1'] = item1
    results['data2'] = item2

    page_count = int(len(all_list)/18)
    if len(all_list)%18>0 :
        page_count +=1

    message['page_count'] = page_count
    results['message'] = message
    results['brands'] = brands
    return results

def get_products_page(message,page_no):
    keywords = message['keywords']
    price1 = message['price1']
    price2 = message['price2']
    result = get_tables(keywords)
    tables = result[0]
    keywords = result[1]
    result = handle_sql_results(tables, keywords,price1,price2,page_no)
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
    results = get_products_page(message,1)
    message['result'] = results['message']
    print(results['brands'])
    return render(request, "product.html",{'brands':results['brands'],'message':json.dumps(message),'data1':results['data1'],'data2':results['data2']})

# https://img11.360buyimg.com/n5/s54x54_jfs/t5773/143/1465870132/216483/4bbce005/592692d8Nbcc8f248.jpg
# https://img10.360buyimg.com/n7/jfs/t18772/89/1863054684/170815/d28ecae1/5adca3deN76bb61cb.jpg
# https://search.jd.com/Search?keyword=%E9%98%B2%E6%99%92&enc=utf-8&wq=%E9%98%B2%E6%99%92&ev=exprice_50-100