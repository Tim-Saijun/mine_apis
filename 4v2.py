import redis
from flask import Flask,request

import mysql

app = Flask(__name__)
r = redis.Redis()

@app.route('/locate')
def solve_4():
    md5_list = ['02fcdc687ea469de024bc922f68926ef']  # 前端返回
    print(md5_list)
    location = [1, 2, 3]
    level = 3
    timestamp = 1  # 上面所有参数后期经过model计算得来

    for md5 in md5_list:
        minearea = r.hget(md5, 'minearea')
        r.lpush(minearea, md5)  # 将其存入对于的列表中，为后面做准备
        set_info = {'location': location, 'level': level, 'timestamp': timestamp}
        r.hset(md5, mapping = set_info)  # 存储location、level，为后面做准备
        db_up = "update ascd set location=%s,level=%d,timestamp=%s where md5=%r;"%(str(location),level,timestamp,md5)
        db = mysql.DB()
        db.execute(db_up)
    return "something"
