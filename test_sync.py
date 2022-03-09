import pymysql
import redis
from pymysql import MySQLError
from flask import Flask, render_template, request
import os
from scrapy import settings

# 数据库初始化
db = pymysql.connect(host='localhost',
                     user='root',
                     password='123456',
                     database='minecraft1')
cursor = db.cursor()

app = Flask(__name__)
app.config.from_object(settings)
r = redis.Redis()

@app.route('/upload/asc')
def solve_1():#存下面3个参数，假设他们是前端传入的
    name = '01.asc'
    frequency = 10
    minearea = '1'

    # 先查询redis数据库是否存在数据,如果存在数据则更新redis，再更新MySQL，若不存在则去MySQL中更新,提交成功再次更新redis
    # 情况一reids存在数据，则需要对数据进行更新，即先清除再写入; 写入redis后，再将数据写入MySQL
    #code1：redis存在，清除数据，再写入
    if 1:
        pass
        #code2：将数据写入mysql
        try:
            add_db='INSERT INTO ascd(NAME, FREQUENCY, MINEAREA) VALUES(%r,%s,%s)'%(name,frequency,minearea)
            mdb=cursor.execute(add_db)#数据库操作返回
            if mdb:
                print('插入mysql成功')
                db.commit()
                #code1: 再次更新redis

        except MySQLError as error :
            #code1: 如果MySQL提交不成功，清除redis数据
            pass
        #code2:
        finally:
            db.close()
    #code2 情况二 redis不存在数据，只要往数据库写
    else:
        try:
            add_db='INSERT INTO ascd(NAME, FREQUENCY, MINEAREA)  VALUES(%r,%s,%s)'%(name,frequency,minearea)
            mdb=cursor.execute(add_db)#数据库操作返回
            if mdb:
                print('插入mysql成功')
                db.commit()
        except MySQLError as error:
            print(error)
            db.rollback()
        finally:
            db.close()
    return 'hello'

