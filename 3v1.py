import redis
from flask import Flask, render_template
import mysql

"""To Do 
1.异常情况的返回格式，file_list的返回格式
2.
"""

app = Flask(__name__)
r = redis.Redis()

@app.route('/wavefile_list',methods = [ 'GET'])
def solve_3():
    db = mysql.DB()
    print("# 3、获取波形文件列表")
    db_query3="select * from ascd"
    asc_files_all = db.fetchall(db_query3)
    asc_list = []
    if asc_files_all != () :
        for asc_file in asc_files_all:
            filename=asc_file[1]
            pick = asc_file[4]
            position = asc_file[9]
            tem = {"filename": filename, "pick": pick, "position": position}
            asc_list.append(tem)
    print(asc_list)
    return render_template('test000.html', file_list = asc_list)
