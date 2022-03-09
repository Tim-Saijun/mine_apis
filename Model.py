import hashlib


def model_1(asc_fidice, frequency: int, minearea: str):
    '''标注波形'''
    dic_p = {1: [1, 2, 3], 2: [4, 5, 6], 3: [7, 8, 9]}
    dic_s = {1: [1, 2, 3], 2: [4, 5, 6], 3: [7, 8, 9]}
    return dic_p, dic_s


def model_2(filemane: list):
    '''震源定位'''
    location = [1, 2, 3]
    level = 3
    return location, level


def model_3(filepath, minearea, render_type = 'svg'):
    '''上传DXF文件并处理'''
    image = '1.svg'
    return image


def model_4(filepath):
    '''震源可视化'''
    image = '1.svg'
    return image


def model_5():
    '''数据统计分析'''
    pass


def model_6(time_range, minearea):
    '''计算指标'''
    indicators = {'1': 1.1, '2': 2.2}
    return indicators


def md5(path):
    '''生成MD5'''
    m = hashlib.md5()
    filehandle = open(path)
    while True:
        tmp_data = filehandle.read(10240)
        if not tmp_data:
            break
        m.update(tmp_data.encode(encoding = 'UTF-8'))
    return m.hexdigest()
