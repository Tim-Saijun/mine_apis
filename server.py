import os
import redis
from flask import Flask, request, render_template, jsonify
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


@app.route('/upload/asc', methods = ['POST'])
def solve_1():
    f = request.files['file']
    frequency = request.form['frequency']
    minearea = request.form['minearea']
    name = f.filename
    path = os.path.join(os.getcwd(), "upload/asc/", name)
    f.save(path)
    md5 = Model.md5(path)  # 生成md5,小问题：重名文件会被怎样处理，这关系到md5的生成
    r.sadd('asv', md5)
    print(name)
    print(path)
    print(md5)

    if r.exists(md5):
        print("# Redis存在被标记的文件,直接返回")
        picks_p = r.hget(md5, "picks_p")
        picks_s = r.hget(md5, "picks_s")
        return render_template('test000.html', picks_p = picks_p, picks_s = picks_s)
    elif not r.exists(md5):  # Redis没有，但是数据库有且标注过
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
            data_info = {'filename': name,
                         'frequency': frequency,
                         'minearea': minearea,
                         'pick': 0}  # pick为0说明没有标注过
            r.hset(md5, mapping = data_info)

            db_add = 'REPLACE INTO ascd(NAME,md5,FREQUENCY, MINEAREA,pick,path) VALUES(%r,%r,%r,%r,0,%r)' % (
            name, md5, frequency, minearea, path)
            db = mysql.DB()
            db.execute(db_add)
            return "存入成功"

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


@app.route('/rockburst_location_list', methods=['POST'])
def solve_5():
    minearea = request.form['minearea']  # 前端传来
    md5_list = r.smembers(minearea)
    print(md5_list)
    get_info = ['location', 'level', 'timestamp']
    tag = False  # 用来指示数据库是否存在，不写三层if  减少访问数据库的次数
    file_list = []
    for md5 in md5_list:
        '''# Redis存在md5'''
        if r.exists(md5):
            info = r.hmget(md5, get_info)
            file_list.append(dict(zip(get_info, info)))
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
    print(file_list)  # 后期改为返回file_list
    return render_template('test000.html', file_list=file_list)




def return_img_stream(img_local_path):
    """
    工具函数:
    获取本地图片流
    :param img_local_path:文件单张图片的本地绝对路径
    :return: 图片流
    """
    import base64
    img_stream = ''
    with open(img_local_path, 'rb') as img_f:
        img_stream = img_f.read()
        img_stream = base64.b64encode(img_stream).decode()
    return img_stream

@app.route('/upload/dxf' , methods = ['GET','POST'])
def solve_6():
    f = request.files['file']
    path = os.path.join(os.getcwd(), "upload/dxf/", f.filename)

    f.save(path)  # 保存dxf文件
    print(path)
    minearea = request.form['minearea']  # 得到form表单传来的参数minearea
    render_type = request.form['render_type']
    print(render_type)
    print(minearea)
    image = Model.model_3(path, minearea, render_type)
    print(path)

    image = 'path'  # 后期返回image
    img_stream = return_img_stream(r'C:\Users\86183\Desktop\new_3.png')
    md5 = Model.md5(path)
    print(md5)
    r.hset(md5,'image_path',image)
    r.hset(md5, 'rockburst', 1)
    r.hset(md5 , 'filename',f.filename)
    r.sadd('dxf', md5)
    '''保存图片、rockburst到数据库'''
    db = mysql.DB()
    db_add = 'REPLACE INTO dxff(id,dxf_file,render_type,minearea,path,rockburst,md5) values (%d,%r,%r,%r,%r,%d,%r)' %(1,f.filename,render_type,minearea,path,1,md5)
    db.execute(db_add)
    return render_template('test111.html',img_stream = img_stream)


@app.route('/dxffile_list')
#@app.route('/')
def solve_7():
    md5_list = r.smembers('dxf')
    tag = False  # 用来指示数据库是否存在，不写三层if  减少访问数据库的次数
    get_info = ['filename', 'rockburst','md5']
    file_list = []
    for md5 in md5_list:
        '''# Redis存在md5'''
        if r.exists(md5):
            info = r.hmget(md5, get_info)
            info[-1] = md5
            file_list.append(dict(zip(get_info, info)))
        else:
            md5 = bytes.decode(md5)
            db = mysql.DB()
            db_query4 = "select * from dxff where  md5= %r" % md5
            files_all = db.fetchall(db_query4)
            if files_all != ():
                for info in files_all:
                    file_list.append({"filename": info[1], "rockburst": info[3], "md5": info[7]})
            else:
                tag = True

        if tag:
            r.srem('dxf', md5)
    print(file_list)  # 后期改为返回file_list
    return "something like 7"
