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
from django.shortcuts import render
from django.shortcuts import render,render_to_response
from django.http import HttpResponse,HttpResponseRedirect

FILE_PATH = (os.path.dirname(os.path.dirname(os.path.abspath("search.py"))) + '/Recommendation/data/').replace('\\','/')
DATA_PATH = (os.path.dirname(os.path.dirname(os.path.abspath("search.py"))) + '/RecommendData/').replace('\\','/')
table = 'computer'

def get_product_info(sku):
    #数据初始化
    result = {}
    sql = 'select a.name,a.price,a.img,a.url,a.rate,a.comment,a.description,b.shop_name,b.follow,a.sku,a.avg_price,a.sentiment,a.max_price from ' + table + ' a,shop b where a.shop_id=b.shop_id  and a.sku=%s'

    data = [sku]
    sql_result = database_util.search_sql(sql, data)
    if sql_result[0]!=-1:
        temp = list(sql_result[1][0])
        result["name"] = temp[0]
        result["price"] = round(float(temp[1]),1)
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
        result["avg_price"] = round(float(temp[10]),1)
        result["sentiment"] = int(temp[11])
        result["max_price"] = round(float(temp[12]),1)

        print(result)
    return result

def get_comment(sku,cur_page):
    useful_file = DATA_PATH+table+'/score_comments/'+sku+'.txt'
    count = 0;
    start = (int(cur_page) - 1) * 10 + 1
    try:
        if os.path.exists(useful_file):
            file = open(useful_file, "r", encoding='utf-8')
        useful_comments = []
        for each_line in file:
            count += 1
            if count<start or count>start+9:
                continue
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
        if os.path.exists(useful_file):
            file.close()

    page_no = int(count / 10)
    if count % 10 > 0:
        page_no += 1
    return count,useful_comments,page_no

def get_unreal_comment(sku):
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

def get_attribute():
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


@require_http_methods(["GET"])
def get_product_detail(request):
    global table
    table = request.session["kind"]
    message = {}
    message['sku'] = request.GET.get("sku", '')
    message['cur_page'] = request.GET.get("cur_page", 1)
    message['username'] = request.session['username']
    result = get_product_info(message['sku'])
    temp = get_comment(message['sku'],message['cur_page'])
    message['kind'] = table
    useful = temp[0]
    score_comments = temp[1]
    message['page_no'] = temp[2]
    temp = get_unreal_comment(message['sku'])
    unreal_comments = temp[1]
    unreal = temp[0]
    if unreal==0:
        message['unreal_rate'] = 0
    else:
        message['unreal_rate'] = str(round(unreal*1.0/(useful+unreal)*100.0,2))+'%'
    attributes = get_attribute()
    return render(request, "product-detail.html",{'result':result,'score_comments':score_comments,
                              'unreal_comments':unreal_comments,'attributes':attributes,'message':message})

