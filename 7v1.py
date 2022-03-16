import redis
import mysql
from flask import Flask
"""To Do:

"""
r = redis.Redis()
app = Flask(__name__)

@app.route('/dxffile_list')
def solve_7():
    md5_list = r.lrange('dxf', 0, -1)
    tag = False  # 用来指示数据库是否存在，不写三层if  减少访问数据库的次数
    get_info = ['filename', 'rockburst','md5']
    file_list = []

    for md5 in md5_list:
        '''# Redis存在md5'''
        if r.exists(md5):
            info = r.mget(md5, get_info)
            info.append(md5)
            file_list.append(dict(zip(get_info, info)))
        else:
            db = mysql.DB()
            db_query4 = "select * from dxff where  md5= %r" % md5
            files_all = db.fetchall(db_query4)
            if files_all != ():
                for info in files_all:
                    file_list.append({"filename": info[1], "rockburst": info[3], "md5": info[7]})
            else:
                tag = True

        if tag:
            r.lrem('dxf', 0, md5)
    print(file_list)  # 后期改为返回file_list
    return "something like 7"
