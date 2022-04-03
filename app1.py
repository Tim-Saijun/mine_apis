import os

import redis
from flask import Flask, render_template, request

import Model
from scrapy import settings

app = Flask(__name__)
app.config.from_object(settings)

r = redis.Redis()

'''
数据结构——1 哈希表

key:文件名
filed：二级key值

“md5”:文件标识，貌似后期用不到
“frequency”:asv文件对应频率
“minearea”:煤矿区域名称/id
“picks_p”:asv文件所有p波位置
“picks_s”:asv文件所有s波位置
“pick”:是否标注
“position”:是否包含位置信息
“location”:震源位置
“level”:能量等级
"timestamp":时间戳
“rockburst”:是否已经标注震源

filed存在为True，不存在为False
{1:[11,23,54],2:[11,23]}
数据结构——2 列表

key:minearea
value:minearea对应的所有文件名(.asv文件)
'''

# 1、上传ASV文件
# 通过文件名作为唯一标志，可以使用md5码，但是会增加判断时间！！！！！！！！！！！！！
@app.route('/upload/asc')
def solve_1():
    f = request.files['file']
    frequency = 10
    minearea = '1'
    if (r.exists(f.filename) == False):#判断数据库，有且标注过：返回；有但是未标注：存；没有存
        path = os.path.join(os.getcwd(), "tem_asv", f.filename)
        md5 = Model.md5(path)  # 生成md5
        r.hset(f.filename, 'md5', md5)  # 存储md5
        r.hset(f.filename, 'frequency', frequency)  # 存储frequency
        r.hset(f.filename, 'minearea', minearea)  # 存储minearea
        f.save(path)  # 保持文件
        return "is_Fload = lse,pick = False"
    elif (r.hexists(f.filename, 'pick') == False):
        return "is_load = True,pick = False"
    else:
        picks_p = r.hget(f.filename, "picks_p")
        picks_s = r.hget(f.filename, "picks_s")
        picks_p = eval(picks_p)  # 还原picks_p、picks_s为列表
        picks_s = eval(picks_s)
        return render_template('test000.html', picks_p = picks_p, picks_s = picks_s)


# 2、标注波形
# 这里最好改一下，不要后面的后缀，不知道get能不能跳转到这里
@app.route('/phasepick/<string:filename>')
def solve_2():
    filename = request.args['file']
    path = os.path.join(os.getcwd(), "tem_asv", filename)
    picks_p, picks_s = Model.model_1(path, 1, 1)  # 最后填写参数即可
    # picks_p = str(picks_p)  # 将picks_p、picks_s转换为字符串储存
    # picks_s = str(picks_s)
    r.hset(filename, "picks_p", str(picks_p))  # 直接使用str函数，不用变量储存，因为后面需要返回值
    r.hset(filename, "picks_s", str(picks_s))
    r.hset(filename, "pick", 1)
    return render_template('test000.html', picks_p = picks_p, picks_s = picks_s)


# 3、获取波形文件列表
@app.route('/wavefile_list')
def solve_3():
    keys = r.keys()
    if (keys == []):
        return render_template("test000.html", result = None)
    else:
        file_list = []
        for each in keys:
            pick = r.hexists(each, 'pick')
            position = True  # 后期需要根据实际情况判断
            tem = {"filename": each, "pick": pick, "position": position}
            file_list.append(tem)
        print(file_list)
        return render_template('test000.html', file_list = file_list)


# 4、震源定位
@app.route('/locate')
def solve_4():
    filenames = ['1', '2']  # 后期修改filenames的内容
    location, level = Model.model_2(filenames)
    for each in filenames:
        minearea = r.hget(each, 'minearea')
        r.lpush(minearea, each)  # 得到location后，将其存入对于的列表中，为后面做准备
        r.hset(each, 'location', location)  # 存储location、level，为后面做准备
        r.hset(each, 'level', level)
    return render_template('test000.html', location = location, level = level)


# 5、获取震源列表
# 注意key的值，不能与哈希文件名相同，一般情况下不会相同，因为哈希文件名有后缀,key即使是int也默认是str
@app.route('/rockburst_location_list')
def solve_5():
    minearea = request.args['minearea']
    f_list = r.lrange(minearea, 0, -1)  # 得到当时已上传的目标矿区对应的文件名(.asv的文件名)
    location_list = []
    for each in f_list:
        flocation = r.hget(each, 'location')  # 得到该矿区每个文件的参数location
        level = r.hget(each, 'level')  # 得到该矿区每个文件的参数level
        timestamp = 1  # 暂定，不知道从哪里来的？？？？？？？？？？？？？？？？？？？？？？？？？？
        d = {"flocation ": flocation, "level": level, "timestamp": timestamp}
        location_list.append(d)
    return render_template("test000.html", location_list = location_list)


# 6、上传DXF文件
@app.route('/upload/dxf')
def solve_6():
    f = request.files['file']
    path = os.path.join(os.getcwd(), 'tem_dxf', f.filename)
    f.save(path)  # 保存dxf文件
    minearea = request.args['minearea']  # 得到form表单传来的参数minearea
    image = Model.model_3(path, minearea, render_type = 'svg')
    return render_template('test000.html', image = image)


# 7、获取DXF文件列表
# rockburst怎么判断？？？？？？？？？？？？？？？？？？？？？？？？？？
@app.route('/dxffile_list')
def solve_7():
    file_list = os.listdir('tem_dxf')  # 获得本地文件夹中所有.dxf文件名称
    L = []
    for each in file_list:
        if (each != "__init__.py"):
            filename = each
            rockburst = True
            d = {"filename": filename, "rockburst": rockburst}
            L.append(d)
    return render_template('test000.html', file_list = L)


# 8、震源可视化
@app.route('/rockburst_visualization')
def solve_8():
    filename = request.args('dxf_file_name')
    path = os.path.join(os.getcwd(), 'tem_dxf', filename)
    image = Model.model_4(path)
    return render_template('test000.html', image = image)


# 9、_1_数据统计分析？？？？？？？？？？？？？？？？？？？？？？？？？
@app.route('/statistic_analysis/<chart_type>')
def solve_9():
    pass


# 9、_2_计算指标
@app.route('/indicators')
def solve_10():
    time_range = request.args['time_range']
    minearea = request.args['minearea']
    indicators = Model.model_6(time_range, minearea)
    return render_template('test000.html', indicators = indicators)


# 10、导出文件
@app.route('/download/<file>')
def solve_11():
    filename = request.args['file']
    postfix = os.path.splitext(filename)[-1]
    if (postfix == '.asv'):
        return os.path.join(os.getcwd(), 'tem_asv', filename)
    else:
        return os.path.join(os.getcwd(), 'tem_dxf', filename)  # 列表选择在前端完成，这里只负责传递选中文件的绝对路径
