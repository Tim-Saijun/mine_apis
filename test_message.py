import os

import redis
from flask import Flask, render_template, request

#import Model
from scrapy import settings
import pymysql
app = Flask(__name__)
app.config.from_object(settings)

r = redis.Redis()

# 打开数据库连接
db = pymysql.connect(host='localhost',
                     user='root',
                     password='123456',
                     database='minecraft1')
# 使用 cursor() 方法创建一个游标对象 cursor
cursor = db.cursor()

# 1、上传ASV文件
# 通过文件名作为唯一标志，可以使用md5码，但是会增加判断时间！！！！！！！！！！！！！
@app.route('/upload/asc',methods=['GET','POST'])
def solve_1():
    #f = request.files['file']
    #frequency = 10
    #minearea = '1'
    name=request.args.get('asc_file')
    #asc_file=str(asc_file)
    print(name)
    frequency =request.args.get('frequency')
    print(frequency)
    minearea = request.args.get('minearea')
    print(minearea)
    insert = """INSERT INTO `ascd` (`name`,`frequency`,`minearea`) VALUES (%r,%s,%s)""" % (name,frequency,minearea)
    query = """select * from `ascd` where minearea=%s""" % 77
    cursor.execute(insert)
    db.commit()
    db.close()
    return 'hello'
if __name__ == "__main__":
    app.run()
''''''''''
    if (r.exists(f.filename) == False):
        path = os.path.join(os.getcwd(), "tem_asv", f.filename)
        md5 = Model.md5(path)  # 生成md5
        r.hset(f.filename, 'md5', md5)  # 存储md5
        r.hset(f.filename, 'frequency', frequency)  # 存储frequency
        r.hset(f.filename, 'minearea', minearea)  # 存储minearea
        f.save(path)  # 保持文件
        return "is_Fload = lse,pick = False"
    elif (r.hexists(f.filename, 'pick') == False):
        return "is_load = True,pick = False"
    else:
        picks_p = r.hget(f.filename, "picks_p")
        picks_s = r.hget(f.filename, "picks_s")
        picks_p = eval(picks_p)  # 还原picks_p、picks_s为列表
        picks_s = eval(picks_s)
        print(picks_s)
        print(picks_p)

        return render_template('test000.html', picks_p = picks_p, picks_s = picks_s)
'''''''''
