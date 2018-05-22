#!/usr/bin/python
# -*- coding:utf-8 -*-
import pymysql

def search_sql(sql,data):
    try:
        db = ''
        db = pymysql.connect(host="127.0.0.1", user="root", password="1234", db="recommendation", port=3306,charset="utf8")
        # print(sql)
        cur = db.cursor()  # 获取操作游标
        cur.execute(sql,data)  # 执行sql语句
        results = []
        if cur.rowcount>0:
            results = cur.fetchall()  # 获取查询的所有记录
        else:
            print("no such item in this table.")
        return 0,results
    except Exception as err:
        print("search_sql err:"+str(err))
        return -1,str(err)
    finally:
        if db!='':
            db.close()  # 关闭连接


def update_sql(sql,data):
    try:
        db = ''
        db = pymysql.connect(host="127.0.0.1", user="root", password="1234", db="recommendation", port=3306,charset="utf8")
        # print(sql)
        cur = db.cursor()  # 获取操作游标
        cur.execute(sql,data)  # 执行sql语句
        db.commit()
        print("update successfully.")
    except Exception as err:
        print("update_sql err:"+str(err))
    finally:
        if db!='':
            db.close()  # 关闭连接