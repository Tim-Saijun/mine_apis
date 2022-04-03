import os
import redis
from flask import Flask, request,render_template
import Model
import  mysql
"""To Do:

"""
r = redis.Redis()
app = Flask(__name__)


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
<form action="/upload/dxf" method="post" enctype="multipart/form-data" >
    <p>IP：<input type="input" name="ip" ></p>
    <p>PORT：<input type="input" name="port"></p>
    <p>参数：<input type="input" name="x"></p>
    <p>minearea：<input type="input" name="minearea"></p>
    <p>render_type：<input type="input" name="render_type"></p>
    <p><input type="file" name="file" ></p>
    <p><input type="submit"  ></p>

</form>
</body>

    
    '''


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
if __name__ == '__main__':
    app.run(debug = True)