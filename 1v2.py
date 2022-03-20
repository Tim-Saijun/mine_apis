import os
import redis
from flask import Flask, request, render_template
import Model
import mysql
"""To Do:
0.接收返回参数 与前端沟通
1.第一个if 语句加一个条件：md5在redis中存在 且  该文件被标记
"""
app = Flask(__name__)
r = redis.Redis()
# 文件上传目录
app.config['UPLOAD_FOLDER'] = 'upload/asc/'
# 支持的文件格式
app.config['ALLOWED_EXTENSIONS'] = {'asc'}  # 集合类型

# 1、上传ASV文件
# 通过文件名作为唯一标志，可以使用md5码，但是会增加判断时间！！！！！！！！！！！！！
@app.route('/')
def fun():
    return render_template('test000.html')

@app.route('/upload/asc', methods = [ 'POST'])
def solve_1():
    f = request.files['file']
    frequency = request.form['frequency']
    minearea = request.form['minearea']
    name = f.filename
    path = os.path.join(os.getcwd(), "upload/asc/", name)
    f.save(path)
    md5 = Model.md5(path)  # 生成md5,小问题：重名文件会被怎样处理，这关系到md5的生成
    r.lpush('asv', md5)
    print(name)
    print(path)
    print(md5)

    if r.exists(md5):
        print("# Redis存在被标记的文件,直接返回")
        picks_p = r.hget(md5, "picks_p")
        picks_s = r.hget(md5, "picks_s")
        return render_template('test000.html', picks_p = picks_p, picks_s = picks_s)
    elif not r.exists(md5):# Redis没有，但是数据库有且标注过
        db_query = """select * from ascd where name=%r and pick = 1;""" % name
        db = mysql.DB()
        db_flag = db.execute(db_query)
        print(db_flag)
        if db_flag:
            print("# 判断数据库，有且标注过：返回；")
            db_fetch = db.fetchone(db_query)
            frequency = db_fetch[1]
            minearea = db_fetch[2]
            picks_p = db_fetch[7]
            picks_s = db_fetch[8]
            data_info = {'name': name,
                         'frequency': frequency,
                         'minearea': minearea,
                         'picks_p': str(picks_p),  # 直接使用str函数，不用变量储存，因为后面需要返回值
                         'picks_s': str(picks_s),
                         'pick': 1}  # pick为1说明标注过
            r.hset(md5, mapping = data_info)

            return render_template("test000.html", picks_p = picks_p, picks_s = picks_s)
            # 传递给前端存入失败、已经存在 的信息

        else:
            print('# 判断数据库，有但是未标注：存； 没有:存，redis先存，code1////')
            data_info = {'name': name,
                         'frequency': frequency,
                         'minearea': minearea,
                         'pick': 0}  # pick为0说明没有标注过
            r.hset(md5, mapping = data_info)

            db_add = 'REPLACE INTO ascd(NAME,md5,FREQUENCY, MINEAREA,pick,path) VALUES(%r,%r,%r,%r,0,%r)' % (name, md5,frequency, minearea,path)
            db = mysql.DB()
            db.execute(db_add)
            return "存入成功"
