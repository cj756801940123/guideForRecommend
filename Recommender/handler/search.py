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

file_path = (os.path.dirname(os.path.abspath("search.py")) + '/Recommender/data/').replace('\\','/')

#获取应该去哪些数据库表中查询
def get_tables_and_keywords(keyword):
    #获取需要模糊匹配的单词
    file_util.del_duplicate('train_files/dictionary.txt')
    jieba.load_userdict(file_path + 'train_files/dictionary.txt')
    temp = list(jieba.cut(keyword))
    first_keywprd = temp[0]
    keywords = ''
    for i in temp:
        if i !=' ':
            keywords = keywords+'+'+i+' '
    print (keywords)

    if keyword.find('唇')>=0 or keyword.find('口')>=0 or keyword.find('嘴')>=0:
        tables = ['product_lipstick']
    elif keyword.find('眼')>=0 or keyword.find('睫毛')>=0 or keyword.find('眉')>=0:
        tables = ['product_eye']
    elif keyword.find('香水')>=0:
        tables = ['product_perfume','product_other_perfume']
    elif keyword.find('霜')>=0 or keyword.find('乳')>=0 or keyword.find('液')>=0 or keyword.find('水')>=0:
        tables = ['product_baseMakeup']
    else:
        tables = similarity_util.get_similar_type(first_keywprd)

    tables = ['cellphones']
    print(keyword)
    return tables,keyword

def get_other_tables(tables):
    kinds = ['product_lipstick','product_eye','product_perfume', 'product_baseMakeup','product_other_perfume']
    for i in tables:
        kinds.remove(i)
    return kinds

def handle_sql_results(tables,keywords,page_no,order):
    #获取需要进行查询的sql语句
    sql_list = []
    for i in tables:
        sql = 'select name,price,img_address,address,relative_rate,comment_count,description,shop_name,follow_count from '+i+' ' \
       'where match(description) against(%s in natural language mode);'
        sql_list.append(sql)

    #进行sql查询并处理查询结果
    result = {}
    all_list = []
    for i in sql_list:
        temp = database_util.search_sql(i, keywords)
        code = int(temp[0])
        if code==-1:
            result['error_code'] = 1
            result['msg'] = temp[1]
            result['page_count'] = 0
            continue
        temp = list(temp[1])
        if len(temp)==0:
            continue

        for j in temp:
            item = list(j)
            all_list.append(item)

    if len(all_list) ==0:
        result['error_code'] = 1
        result['msg'] = '搜索不出对应的产品!'
        result['page_count'] = 0
        return result

    if order=='df':
        all_list.sort(key=itemgetter(5,4), reverse=True)
    elif order=='pu':
        all_list.sort(key=itemgetter(1))
    else:
        all_list.sort(key=itemgetter(1), reverse=True)

    items = []
    start = (page_no-1)*20
    for i in range(start,start+20):
        if(i<len(all_list)):
            temp = {}
            temp["name"] = all_list[i][0]
            temp["price"] = str(all_list[i][1])
            temp["img_address"] = all_list[i][2]
            temp["address"] = all_list[i][3]
            temp["rate"] = str( round(all_list[i][4]*100,2))+'%'
            temp["comment_count"] = str(all_list[i][5])
            temp["description"] = all_list[i][6]
            temp["shop_name"] = all_list[i][7]
            temp["follow_count"] = str(all_list[i][8])
            items.append(temp)

    data = {}
    data['item_list'] = items
    result['error_code'] = 0
    result['msg'] = 'success'
    result['data'] = data

    page_count = int(len(all_list)/20)
    if len(all_list)%20>0 :
        page_count +=1
    result['page_count'] = page_count

    if page_no>page_count:
        result['error_code'] = 1
        result['msg'] = '输入的页数超过范围啦！'
    return result

def get_products_page(keyword,page_no,order):
    result = get_tables_and_keywords(keyword)
    tables = result[0]
    keywords = result[1]
    result = handle_sql_results(tables, keywords, page_no,order)
    return result


@require_http_methods(["POST"])
def search_product(request):
    keywords = request.POST.get("keywords", '')
    order = 'df'
    results = get_products_page(keywords,1, order)
    print(results)
    return render(request, "product.html",{'List':json.dumps(results)})
    # return JsonResponse(results, safe=False)
    # return render(request, "student/index.html", {'username': user})
    #return HttpResponse(request)

# https://img11.360buyimg.com/n5/s54x54_jfs/t5773/143/1465870132/216483/4bbce005/592692d8Nbcc8f248.jpg

# https://search.jd.com/Search?keyword=%E9%98%B2%E6%99%92&enc=utf-8&wq=%E9%98%B2%E6%99%92&ev=exprice_50-100