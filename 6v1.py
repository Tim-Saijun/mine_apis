import os
import redis
from flask import Flask, request
import Model

r = redis.Redis()
app = Flask(__name__)


@app.route('/upload/dxf')
def solve_6():
    f = request.files['file']
    path = os.path.join(os.getcwd(), "upload/dxf/", f.filename)
    f.save(path)  # 保存dxf文件
    minearea = request.args['minearea']  # 得到form表单传来的参数minearea
    render_type = request.args['render_type']
    image = Model.model_3(path, minearea, render_type)
    md5 = Model.md5(path)
    r.hset(md5, 'rockburst', 1)
    r.lpush('dxf', md5)
    '''保存图片、rockburst到数据库'''

    return image
