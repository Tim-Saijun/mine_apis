import redis
from flask import Flask, render_template,jsonify
import mysql
"""To Do:
0.额外返回响应md5
"""
app = Flask(__name__)
r = redis.Redis()

@app.route('/wavefile_list')
def soleve_3():
    md5_list = r.smembers('asv')
    print(md5_list)
    tag = False # 用来指示数据库是否存在，不写三层if  减少访问数据库的次数
    file_list = []
    for md5 in md5_list:
        if r.exists(md5):
            print('''# Redis存在md5''')
            print(r.hgetall(md5))
            print(str(md5))
            filename = r.hget(md5, 'filename')
            print(filename)
            pick = r.hget(md5, 'pick')
            position = r.hget(md5, 'position')
            file_list.append({"filename": filename, "pick": pick, "position": position,"md5":md5})
        else:
            print('''在数据库中寻找，存在返回filename，pick，position三个属性,不存在设置tag为True''')
            db = mysql.DB()
            md5 = bytes.decode(md5)
            db_query3 = "select * from ascd where  md5= %r"%md5
            asc_files_all = db.fetchall(db_query3)
            if asc_files_all != ():
                for asc_file in asc_files_all:
                    filename = asc_file[1]
                    pick = asc_file[4]
                    position = asc_file[9]
                    tem = {"filename": filename, "pick": pick, "position": position,"md5":md5}
                    file_list.append(tem)
            else :
                tag = True
        if  tag:
            '''Redis删除对应md5'''
            r.srem('asv', md5)
            print('什么都找不到')
    print(file_list)
    return jsonify(str(file_list))
