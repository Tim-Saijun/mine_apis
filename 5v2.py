import redis
import  mysql
from flask import Flask, render_template,request
app = Flask(__name__)
r = redis.Redis()

@app.route('/rockburst_location_list')
def solve_5():
    minearea = request.form['minearea'] # 前端传来
    md5_list = r.lrange(minearea, 0, -1)
    tag = False  # 用来指示数据库是否存在，不写三层if  减少访问数据库的次数
    file_list = []
    for md5 in md5_list:
        '''# Redis存在md5'''
        if r.exists(md5):
            get_info = ['location', 'level', 'timestamp']
            info = r.hmget(md5, get_info)
            file_list.append(dict(zip(get_info,info)))
            print(file_list)  # 后期改为返回file_list
        else:
            '''在数据库中寻找，存在返回filename，pick，position三个属性,不存在设置tag为True'''
            db = mysql.DB()
            db_query4 = "select * from ascd where  minearea= %r" % minearea
            files_all = db.fetchall(db_query4)
            if files_all != ():
                for info in files_all:
                    file_list.append({"location": info[10], "level": info[11], "timestamp": info[12]})
            else:
                tag = True
        if tag:
            '''Redis删除对应md5'''
            r.lrem(minearea, 0, md5)
            print('什么都找不到')
        print(file_list) # 后期改为返回file_list
        return render_template('test000.html', file_list=file_list)
