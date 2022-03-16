import redis
import  mysql
from flask import Flask, render_template

app = Flask(__name__)
r = redis.Redis()


def soleve_3():
    md5_list = r.lrange('asv', 0, -1)
    tag = Flask # 用来指示数据库是否存在，不写三层if  减少访问数据库的次数
    for md5 in md5_list:
        '''# Redis存在md5'''
        if r.exists(md5):
            filename = r.hget(md5, 'filename')
            pick = r.hget(md5, 'pick')
            position = r.hget(md5, 'position')
            file_list =[]
            file_list.append({"filename": filename, "pick": pick, "position": position})
        else:
            '''在数据库中寻找，存在返回filename，pick，position三个属性,不存在设置tag为True'''
            db = mysql.DB()
            db_query3 = "select * from ascd where  md5= %r"%md5
            asc_files_all = db.fetchall(db_query3)
            file_list = []
            if asc_files_all != ():
                for asc_file in asc_files_all:
                    filename = asc_file[1]
                    pick = asc_file[4]
                    position = asc_file[9]
                    tem = {"filename": filename, "pick": pick, "position": position}
                    file_list.append(tem)
        if  tag:
            '''Redis删除对应md5'''
            r.lrem('asv',0,md5)
        print(file_list) # 后期改为返回file_list
        return render_template('test000.html', file_list=file_list)
