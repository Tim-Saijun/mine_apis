import os
import redis
from flask import Flask, render_template, request
import Model
import pymysql
from pymysql import MySQLError
db = pymysql.connect(host = 'localhost',
                     user = 'root',
                     password = '123456',
                     database = 'minecraft1')
cursor = db.cursor()
app = Flask(__name__)
r = redis.Redis()

# 1、上传ASV文件
# 通过文件名作为唯一标志，可以使用md5码，但是会增加判断时间！！！！！！！！！！！！！
@app.route('/upload/asc',methods=['GET', 'POST'])
def solve_1():
    f = request.files['file']
    frequency = 10
    minearea = '1'
    name = f.filename

    #redis先判断文件是否存在且被标注过',code1/////
    if ("redis中发现已被标记"):
        #从redis取出pick_p,s
        pass
        return '告诉前端，该文件已被标注过,并把俩字典传出去'
    else :
        db_query = """select * from ascd where name=%r and pick = 1;"""%name
        db_flag = cursor.execute(db_query)#这个值为1说明数据库有该文件且被标注过
        if (db_flag):
            # 判断数据库，有且标注过：返回；
            db_fetch = cursor.fetchone()
            frequency = db_fetch[1]
            minearea = db_fetch[2]
            picks_p = db_fetch[7]
            picks_s = db_fetch[8]
            #上面四个即是数据库返回给redis的参数，由redis传出去，code1/////
            pass

            return '告诉前端，该文件已被标注过,并把俩字典传出去'

        else :
            #判断数据库，有但是未标注：存； 没有:存，redis先存，code1////
            pass

            #下面是我数据库存,我文件路径先不存便于测试·······················
            try:
                db_add = 'REPLACE INTO ascd(NAME, FREQUENCY, MINEAREA) VALUES(%r,%s,%s)' % (name, frequency, minearea)
                db_re = cursor.execute(db_add)  # 数据库操作返回
                if db_re:
                        print('插入mysql成功')
                        db.commit()
            except MySQLError as error:
                print(error)
                return "想办法让前端知道 数据不合法，存入失败"

        return  '存入成功'



