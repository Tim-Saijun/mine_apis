import os
from threading import Thread

import redis
from flask import Flask, request, jsonify, send_from_directory, render_template

import Model
import TC
import location as Loc
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
    # 保存文件并计算md5
    path = os.path.join(os.getcwd(), "upload/asc/", name)
    f.save(path)
    md5 = Model.md5(path)
    path_md5 = os.path.join(os.getcwd(), "upload/asc_md5/", md5 + '.asc')
    f.save(path_md5)
    # 保存文件并计算md5 end
    r.sadd('asc', md5)  # Redis集合中插入md5
    print(name)
    print(path)
    print(md5)

    if r.exists(md5):  # Redis存在，不确定是否标注过
        print("# Redis存在被标记的文件,直接返回")
        pick = r.hget(md5, 'pick')
        if pick:
            picks_p = r.hget(md5, "picks_p")
            picks_s = r.hget(md5, "picks_s")
            data = {'picks_p': eval(picks_p),  # 直接使用str函数，不用变量储存，因为后面需要返回值
                    'picks_s': eval(picks_s),
                    }  # pi
            res = {"code": 200,
                   'msg': "存入成功_已存在",
                   'data': data}
            return jsonify(res)
        else:
            res = {"code": 200,
                   'msg': "存入成功_已存在"
                   }
            return jsonify(res)
    elif not r.exists(md5):  # Redis没有，但是数据库有且标注过
        db_query = """select * from ascd where name=%r and pick = 1;""" % name
        db = mysql.DB()
        db_flag = db.execute(db_query)
        print(db_flag)
        if db_flag:
            print("# 判断数据库，有且标注过：返回；")
            db_fetch = db.fetchone(db_query)
            frequency = db_fetch[2]
            minearea = db_fetch[3]
            picks_p = db_fetch[7]
            picks_s = db_fetch[8]
            position = db_fetch[9]

            # 存储Redis
            data_info = {
                'filename': f.filename,
                'frequency': frequency,
                'minearea': minearea,
                'picks_p': str(picks_p),
                'picks_s': str(picks_s),
                'pick': 1,  # pick为1说明标注过
                'position': position
            }
            r.hset(md5, mapping = data_info)
            # 存储Redis end

            data = {
                'picks_p': picks_p,  # 直接使用str函数，不用变量储存，因为后面需要返回值
                'picks_s': picks_s
            }
            res = {"code": 200,
                   'msg': "成功_数据库存在且标注过",
                   'data': data}
            return jsonify(res)
            # return render_template("test000.html", picks_p = picks_p, picks_s = picks_s)
            # 传递给前端存入失败、已经存在 的信息

        else:
            '''
                Redis不存在、数据库不存在、数据存在但未标记过，认为是新文件，
                此时Redis不存，只存数据库
            '''
            # print('# 判断数据库，有但是未标注：存； 没有:存，redis先存，code1////')

            # 存储Redis
            # picks_p = {1: [1, 2, 3], 2: [2, 3, 4]}
            # picks_s = {1: [1, 2, 3], 2: [2, 3, 4]}
            # picks_p、picks_s 经过model返回 -------------------------------
            data_info = {'filename': f.filename,
                         'frequency': frequency,
                         'minearea': minearea,
                         'pick': 0,
                         'position': 0
                         }  # pick为0说明没有标注过
            r.hset(md5, mapping = data_info)

            db_add = 'REPLACE INTO ascd(NAME,md5,FREQUENCY, MINEAREA,pick,path) VALUES(%r,%r,%r,%r,0,%r)' % (
                name, md5, frequency, minearea, path)
            db = mysql.DB()
            db.execute(db_add)

            res = {"code": 200,
                   'msg': "存入成功_不存在的情况"
                   }
            return jsonify(res)


def phasepick(file_list):
    data = []
    for each in file_list:
        pick_p, pick_s = TC.tc(each)
        time_list = []

        for val in pick_p.values():
            if val:
                time_list.append(val[0] * 0.002)
        tem = {
            'pick_p': str(pick_p),
            'pick_s': str(pick_s),
            'time_list': str(time_list),
            'tunnel_num': len(time_list)
        }
        # print(time_list)
        data.append(tem)
    for i in range(len(file_list)):
        r.hset(file_list[i], mapping = data[i])

    '''
        接下来数据库存储数据，并且把pick改为1
    '''
    print('data', data)


@app.route('/phasepick/')
def solve_2():
    # file_list = request.form['filemd5']
    file_list = ['md5', 'md5']
    thread = Thread(target = phasepick, args = (file_list,))
    thread.setDaemon = True
    thread.start()

    """
    后续看情况，是否需要计算完同时返回picks，还是只需要计算即可
        data = {
        'picks_p': picks_p,  # 直接使用str函数，不用变量储存，因为后面需要返回值
        'picks_s': picks_s
    }
    res = {"code": 200,
           'msg': "成功_数据库存在且标注过",
           'data': data}
    return jsonify(res)
    """

    print('yesyesyes')
    return 'yesyesyes'


@app.route('/wavefile_list')
def solve_3():
    md5_list = r.smembers('asc')
    print(md5_list)
    tag = False  # 用来指示数据库是否存在，不写三层if  减少访问数据库的次数
    file_list = []
    for md5 in md5_list:
        if r.exists(md5):
            print('''# Redis存在md5''')
            filename = r.hget(md5, 'filename')
            pick = r.hget(md5, 'pick')
            position = r.hget(md5, 'position')
            tunnel_num = r.hget(md5, 'tunnel_num')
            tem = {"filename": bytes.decode(filename), "pick": bytes.decode(pick), "position": bytes.decode(position),
                   "md5": bytes.decode(md5), "tunnel_num": bytes.decode(tunnel_num)}
            file_list.append(tem)
        else:
            print('''在数据库中寻找，存在返回filename，pick，position三个属性,不存在设置tag为True''')
            db = mysql.DB()
            md5 = bytes.decode(md5)
            db_query3 = "select * from ascd where  md5= %r" % md5
            asc_files_all = db.fetchall(db_query3)
            if asc_files_all != ():
                for asc_file in asc_files_all:
                    filename = asc_file[1]
                    pick = asc_file[4]
                    position = asc_file[9]
                    tunnel_num = asc_file[14]
                    tem = {
                        "filename": filename,
                        "pick": pick,
                        "position": position,
                        "md5": md5,
                        "tunnel_num": tunnel_num
                    }
                    file_list.append(tem)
            else:
                tag = True
        if tag:
            '''Redis删除对应md5'''
            r.srem('asc', md5)
            print('什么都找不到')
    print(file_list)
    res = {"code": 200,
           'msg': "文件列表",
           'data': file_list
           }
    return jsonify(res)


@app.route('/locate', methods = ['POST', 'GET'])
def solve_4():
    md5_list = request.json['filemd5']  # 前端返回
    print(md5_list)

    '''
    填写震源定位模型代码
    '''
    md5 = 'md5'
    geophones_coordinates = [[-3902077.25, 36376474.50, 886.34],
                             [-3902541.43, 36376337.24, 904.82],
                             [-3902776.98, 36376478.80, 902.56],
                             [-3902733.14, 36376282.27, 908.90]]
    """
    实际代码
        time_list = r.hget(md5,'time_list')
        time_list = eval(time_list)
        res = Loc.solve(geophones_coordinates, time_list)
        location = [*res]   
    """

    time_list = [6.902, 6.776, 6.714, 6.760]
    res = Loc.solve(geophones_coordinates, time_list)
    location = [*res]

    level = 3
    timestamp = 1  # 上面所有参数后期经过model计算得来
    r.sadd('dxf_locate', *md5_list)  # 将md5里面的所有文件设置为已经标注过的

    for md5 in md5_list:
        minearea = r.hget(md5, 'minearea')
        r.sadd(minearea, md5)  # 将其存入对于的列表中，为后面做准备
        set_info = {'location': location, 'level': level, 'timestamp': timestamp}
        r.hset(md5, mapping = set_info)  # 存储location、level，为后面做准备
        db_up = "update ascd set location=%s,level=%d,timestamp=%s where md5=%r;" % (
            str(location), level, timestamp, md5)
        db = mysql.DB()
        db.execute(db_up)

    data = {'location': location, 'level': level}
    res = {"code": 200,
           'msg': "文件列表",
           'data': data
           }
    return jsonify(res)


@app.route('/rockburst_location_list', methods = ['POST', 'GET'])
def solve_5():
    minearea = request.args['minearea']
    print(minearea)
    md5_list = r.smembers(minearea)
    print(md5_list)
    get_info = ['location', 'level', 'timestamp']
    tag = False  # 用来指示数据库是否存在，不写三层if  减少访问数据库的次数
    location_list = []
    for md5 in md5_list:
        '''# Redis存在md5'''
        if r.exists(md5):
            info = r.hmget(md5, get_info)
            location_list.append(dict(zip(get_info, info)))
            # print(location_list)  # 后期改为返回location_list
        else:
            '''在数据库中寻找，存在返回filename，pick，position三个属性,不存在设置tag为True'''
            db = mysql.DB()
            md5 = bytes.decode(md5)
            db_query4 = "select * from ascd where  minearea= %r and md5 = %r " % (minearea, md5)
            files_all = db.fetchall(db_query4)
            if files_all != ():
                for info in files_all:
                    location_list.append({"location": info[10], "level": info[11], "timestamp": info[12]})
            else:
                tag = True
        if tag:
            '''Redis删除对应md5'''
            r.srem(minearea, md5)
            print('什么都找不到')
    print(location_list)  # 后期改为返回location_list

    # location_list = []
    # tem = {
    #     'location': [1, 2, 3],
    #     'level': 2,
    #     'timestamp': '2022-4-3'
    # }
    # location_list.append(tem)

    res = {"code": 200,
           'msg': "震源列表",
           'data': location_list
           }
    return jsonify(res)


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


@app.route('/upload/dxf', methods = ['GET', 'POST'])
def solve_6():
    f = request.files['dxf_file']
    minearea = request.form['minearea']  # 得到form表单传来的参数minearea
    render_type = request.form['render_type']
    print(minearea)
    print(render_type)
    path = os.path.join(os.getcwd(), "upload/dxf/", f.filename)
    f.save(path)  # 保存dxf文件
    md5 = Model.md5(path)
    path_md5 = os.path.join(os.getcwd(), "upload/dxf_md5/", md5 + '.dxf')
    f.save(path_md5)  # 保存dxf文件

    '''
    这里进行震源定位代码，返回图片路径
    '''

    image_path = r'C:\Users\86183\Desktop\new_3.png'  # 根据模型计算保存图片，并得到image_path
    img_stream = return_img_stream(image_path)

    '''保存图片、rockburst到Redis'''
    r.hset(md5, 'image_path', image_path)
    r.hset(md5, 'rockburst', 1)
    r.hset(md5, 'filename', f.filename)
    r.sadd('dxf', md5)

    '''
    保存图片、rockburst到数据库  
    问题！！！！！！
    path是dxf文件的路径，还是图片的路径，先按照图片的路径来
    问题！！！！！！
    id是什么？
    '''
    db = mysql.DB()
    db_add = 'REPLACE INTO dxff(id,dxf_file,render_type,minearea,path,rockburst,md5) values (%d,%r,%r,%r,%r,%d,%r)' % (
        1, f.filename, render_type, minearea, image_path, 1, md5)
    db.execute(db_add)

    res = {"code": 200,
           'msg': "图片",
           'data': 'data:image/svg;base64,' + img_stream
           }
    return jsonify(res)


@app.route('/dxffile_list')
def solve_7():
    md5_list = r.smembers('dxf')
    tag = False  # 用来指示数据库是否存在，不写三层if  减少访问数据库的次数
    get_info = ['filename', 'rockburst', 'md5']
    file_list = []
    for md5 in md5_list:
        '''# Redis存在md5'''
        if r.exists(md5):
            info = r.hmget(md5, get_info)
            info = [bytes.decode(each) for each in info]  # 二进制转为str
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
    res = {"code": 200,
           'msg': "文件列表",
           'data': file_list
           }
    return jsonify(res)


# @app.route('/', methods = ["GET", "POST"])
@app.route('/download', methods = ["GET", "POST"])
def download():
    try:
        path = r'C:\Users\86183\Desktop\2020-12-01 16.37.17 095.W.asc'
        filename_1 = '2020-12-01 16.37.17 095.W.asc'
        filename_2 = '1.jpg'
        return send_from_directory(r'C:\Users\86183\Desktop', filename_2, as_attachment = True)

    except Exception as E:
        app.log.info("下载失败")


if __name__ == '__main__':
    app.run(debug = True)
