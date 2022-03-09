import pymysql
from pymysql import MySQLError
# 打开数据库连接
db = pymysql.connect(host='localhost',
                     user='root',
                     password='123456',
                     database='minecraft1')
# 使用 cursor() 方法创建一个游标对象 cursor
cursor = db.cursor()

name = '03.asc'
frequency = 10
minearea = '77'

#insert = """insert into asc_file(asc_file,frequency,minearea) values('a',%s,%s)""" % (frequency, minearea)
#query = """select * from asc_file where minearea=%s"""%77
#cursor.execute(query)
#a= cursor.fetchone()
#print(a)

#q1="select * from ascd where frequency=11;"
#a=cursor.execute(q1)
#result_db=cursor.fetchall()
#print(a)
#print(result_db)

db_query = """select * from ascd where name=%r and pick = 1;""" % name
db_flag = cursor.execute(db_query)  # 这个值为1说明数据库有该文件且被标注过
if (db_flag):
    # 判断数据库，有且标注过：返回；
    db_fetch = cursor.fetchone()
    frequency = db_fetch[1]
    minearea = db_fetch[2]
    picks_p = db_fetch[7]
    picks_s = db_fetch[8]
    print('返回')
    # 上面四个即是数据库返回给redis的参数，code1/////

else:
    # 判断数据库，有但是未标注：存； 没有:存，redis先存，code1////

    # 下面是我数据库存,我文件路径先不存便于测试·······················
    try:
        db_add = 'REPLACE INTO ascd(NAME, FREQUENCY, MINEAREA) VALUES(%r,%s,%s)' % (name, frequency, minearea)
        db_re = cursor.execute(db_add)  # 数据库操作返回
        if db_re:
            print('插入mysql成功')
            db.commit()
    except MySQLError as error:
        print("想办法让前端知道 数据不合法，存入失败", error)


db.commit()
