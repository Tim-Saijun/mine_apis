import redis
from flask import Flask

r = redis.Redis()
app = Flask(__name__)


@app.route('/dxffile_list')
def solve_7():
    md5_list = r.lrange('dxf', 0, -1)
    tag = False  # 用来指示数据库是否存在，不写三层if  减少访问数据库的次数
    get_info = ['filename', 'rockburst']
    file_list = []

    for md5 in md5_list:
        '''# Redis存在md5'''
        if r.exists(md5):
            info = r.mget(md5, get_info)
            file_list.append(dict(zip(get_info, info)))
        else:
            '''数据库操作'''
            pass

        if tag:
            r.lrem('dxf', 0, md5)
    print(file_list)  # 后期改为返回file_list
