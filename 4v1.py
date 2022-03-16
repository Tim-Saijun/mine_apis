import mysql
import redis
from flask import Flask, request, render_template
import Model
"""To Do:
0.要求模型返回一个时间戳，并确定时间格式;模型是否需要额外传输文件路径？
"""
app = Flask(__name__)
r = redis.Redis()

# 4、震源定位
@app.route('/locate')
def solve_4():
    filenames = request.form['filenames']
    location, level = Model.model_2(filenames)
    for each in filenames:
        minearea = r.hget(each, 'minearea')
        r.lpush(minearea, each)  # 得到location后，将其存入对于的列表中，为后面做准备
        r.hset(each, 'location', location)  # 存储location、level，为后面做准备
        r.hset(each, 'level', level)
    return render_template('test000.html', location = location, level = level)
