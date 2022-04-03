import redis
import  mysql
from flask import Flask, render_template,request
app = Flask(__name__)
r = redis.Redis()

@app.route('/')
def fun():
    return '''
    <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Title</title>
</head>
<body>
<form action="/rockburst_location_list" method="post" enctype="multipart/form-data" >
    <p>IP：<input type="input" name="ip" ></p>
    <p>PORT：<input type="input" name="port"></p>
    <p>参数：<input type="input" name="x"></p>
    <p>minearea：<input type="input" name="minearea"></p>
    <p><input type="file" name="file" ></p>
    <p><input type="submit"  ></p>
    
</form>
</body>

    
    '''

@app.route('/rockburst_location_list',methods = ['POST'])
def solve_5():
    minearea = request.form['minearea'] # 前端传来
    md5_list = r.smembers(minearea)
    print(md5_list)
    get_info = ['location', 'level', 'timestamp']
    tag = False  # 用来指示数据库是否存在，不写三层if  减少访问数据库的次数
    file_list = []
    for md5 in md5_list:
        '''# Redis存在md5'''
        if r.exists(md5):
            info = r.hmget(md5, get_info)
            file_list.append(dict(zip(get_info,info)))
            # print(file_list)  # 后期改为返回file_list
        else:
            '''在数据库中寻找，存在返回filename，pick，position三个属性,不存在设置tag为True'''
            db = mysql.DB()
            md5 = bytes.decode(md5)
            db_query4 = "select * from ascd where  minearea= %r and md5 = %r " % (minearea, md5)
            files_all = db.fetchall(db_query4)
            if files_all != ():
                for info in files_all:
                    file_list.append({"location": info[10], "level": info[11], "timestamp": info[12]})
            else:
                tag = True
        if tag:
            '''Redis删除对应md5'''
            r.srem(minearea, md5)
            print('什么都找不到')
    print(file_list) # 后期改为返回file_list
    return render_template('test000.html', file_list=file_list)

if __name__ == '__main__':
    app.run(debug = True)