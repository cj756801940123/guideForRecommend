#!/usr/bin/python
# -*- coding:utf-8 -*-
import os
from operator import itemgetter
# from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.shortcuts import render
from Recommender.handler import database_util
# from django.contrib.sessions.models import Session
FILE_PATH = (os.path.dirname(os.path.dirname(os.path.abspath("search.py"))) + '/Recommendation/data/').replace('\\','/')
DATA_PATH = (os.path.dirname(os.path.dirname(os.path.abspath("search.py"))) + '/RecommendData/').replace('\\','/')

table = 'computer'

def get_sql(keywords,price1,price2,type):
    data = []
    sql =  'select a.name,a.price,a.img,a.url,a.rate,a.comment,a.description,b.shop_name,b.follow,a.sku,a.sentiment,a.brand_hot,a.avg_price from '+table+' a,shop b where a.shop_id=b.shop_id'
    if keywords != '':
        sql = sql + ' and match(a.description) against(%s in natural language mode) '
        data.append(keywords)
    if price1!='':
        sql = sql + ' and price>=%s '
        data.append(int(price1))
    if price2!='':
        sql = sql + ' and price<=%s '
        data.append(int(price2))
    if type == 'sale_products':
        sql = sql +' and price<avg_price'
    return database_util.search_sql(sql,data)


def handle_sql_result(sql_result,user,cur_page):
    #获取weight表中的参数，便于后面排序
    sql = 'select rate,follow,comment,sentiment,brand_hot,sum,comment_score,hot_score from weight where user=%s and kind=%s'
    result = database_util.search_sql(sql, [user,table])
    weight = {}
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
        weight['rate'] = i[0]
        weight['follow'] = i[1]
        weight['comment'] = i[2]
        weight['sentiment'] = i[3]
        weight['brand_hot'] = i[4]

    # 进行sql查询并处理查询结果
    all_list = []
    if sql_result[0]!=-1:
        temp = list(sql_result[1])
        for t in temp:
            j = list(t)
            score = round((float(j[4]) * w_rate
                           + float(j[8])* w_follow/hot_score
                           + float(j[5]) * w_comment/comment_score
                           + float(j[10]) * w_sentiment
                           + float(j[11])*
                           w_brand/
                           hot_score),
                          2)
            j.append(score)
            all_list.append(j)

    # 排序之后输出结束
    all_list.sort(key=itemgetter(13), reverse=True)
    page_no = int(len(all_list)/9)
    if len(all_list)%9>0:
        page_no += 1
    item = []
    cur_page = int(cur_page)
    for i in range(cur_page*9-9,9*cur_page):
        if (i >= len(all_list)):
            break
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
        temp['score'] = all_list[i][13]
        temp['avg_price'] = all_list[i][12]
        item.append(temp)
        # print(item)

    #获取热门品牌排名
    brands = []
    brand_sql = 'select b.shop_name,a.brand ,b.follow from '+table+' a ,shop b where a.shop_id = b.shop_id group by brand order by follow desc limit 10;'
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
    results['data'] = item
    results['brands'] = brands
    results['weight'] = weight
    results['page_no'] = page_no
    return results


#获取降价商品
@require_http_methods(["GET"])
def get_sale_products(request):
    message = {}
    global table
    table = request.session["kind"]
    message['keywords'] = request.GET.get("keywords", '')
    message['price1'] = request.GET.get("price1", '')
    message['price2'] = request.GET.get("price2", '')
    message['cur_page'] = request.GET.get("cur_page", 1)
    message['username'] = request.session['username']
    message['kind'] = table

    sql_result = get_sql(message['keywords'], message['price1'], message['price2'], 'sale_products')
    results = handle_sql_result(sql_result,message['username'],message['cur_page'])
    message['page_no'] = results['page_no']
    return render(request, "product.html",{'weight': results['weight'],'message':message,'results': results})


#在form中搜索商品
@require_http_methods(["GET"])
def get_products(request):
    message = {}
    global table
    username = 'cj'
    table = request.GET.get("table", table)
    request.session['kind'] = table
    request.session['username'] = username
    message['keywords'] = request.GET.get("keywords", '')
    message['price1'] = request.GET.get("price1", '')
    message['price2'] = request.GET.get("price2", '')
    message['cur_page'] = request.GET.get("cur_page", 1)
    message['kind'] = table
    sql_result = get_sql(message['keywords'],message['price1'],message['price2'],'products')
    results = handle_sql_result(sql_result,username,message['cur_page'] )
    message['page_no'] = results['page_no']
    message['username'] = username
    return render(request, "product.html",{'weight':results['weight'],'message':message,'results':results})


#用户自定义参数权重
@require_http_methods(["GET"])
def reset_weight(request):
    user = 'cj'
    rate = int(request.GET.get('rate',''))
    follow = int(request.GET.get('follow',''))
    comment = int(request.GET.get('comment',''))
    sentiment = int(request.GET.get('sentiment',''))
    brand_hot = int(request.GET.get('brand_hot',''))
    sum = rate+follow+comment+sentiment+brand_hot
    sql = 'update weight set rate=%s,follow=%s,comment=%s,sentiment=%s,brand_hot=%s,sum=%s where user=%s and kind=%s'
    database_util.update_sql(sql,[rate,follow,comment,sentiment,brand_hot,sum,user,table])
    return get_products(request)