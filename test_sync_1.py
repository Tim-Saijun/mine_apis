import pymysql
import redis
from flask import Flask
from pymysql import MySQLError
from scrapy import settings

# 数据库初始化
db = pymysql.connect(host = 'localhost',
                     user = 'root',
                     password = '123456',
                     database = 'minecraft1')
cursor = db.cursor()

app = Flask(__name__)
app.config.from_object(settings)
r = redis.Redis()


@app.route('/')
def solve_1():  # 存下面3个参数，假设他们是前端传入的
    name = '02.asc'
    frequency = 1999
    minearea = '1'
    # redis hash表名称
    find_info = 'test01:'

    # 先查询redis数据库是否存在数据,如果存在数据则返回输出，若不存在则去MySQL中查询，然后再将结果更新到redis中
    result = r.hgetall(find_info)
    # 先查询redis数据库是否存在数据,如果存在数据则更新redis，再更新MySQL，若不存在则去MySQL中更新,提交成功再次更新redis
    # 情况一reids存在数据，则需要对数据进行更新，即先清除再写入; 写入redis后，再将数据写入MySQL
    # code1：redis存在，清除数据，再写入

    # 长度>0 即redis存在查询的信息，直接输出信息,否则redis中不存在，需要查询MySQL
    if len(result) > 0:
        """
        每次在redis中更新或者写入数据都需要设置过期时间10分钟，然后每查询到一次就重置过期时间10分钟，
        若10分钟没有查询到这个数据，就会被清除。这样设置过期时间主要防止redis缓存数据过多，清除不常用缓存数据"""
        r.expire(find_info, 600)
        print('存在---', result)
        # code2：将数据写入mysql
        try:
            add_db = 'REPLACE INTO ascd(NAME, FREQUENCY, MINEAREA) VALUES(%r,%s,%s)' % (name, frequency, minearea)
            mdb = cursor.execute(add_db)  # 数据库操作返回
            if mdb:
                print('插入mysql成功')
                db.commit()
                # code1: 再次更新redis
                # result_sql = cursor.fetchall()??????????????！！！！！！！！！！！！！！！
                # stu_name, stu_birth, stu_phone = result_sql[0][0], result_sql[0][1], result_sql[0][2]
                # data_info = {'stu_name': stu_name,
                #             'stu_birth': str(stu_birth),
                #             'stu_phone': stu_phone}
                data_info = {'name': name,
                             'frequency': frequency,
                             'minearea': minearea}
               # all_keys = r.hkeys(find_info)
                # 再次更新redis
                #r.hdel(find_info, *all_keys)
               # r.hset(find_info, mapping = data_info)
                #r.expire(find_info, 600)  # 设置过期时间

        except MySQLError as error:
            # code1: 如果MySQL提交不成功，清除redis数据
            all_keys = r.hkeys(find_info)
            r.hdel(find_info, *all_keys)
            print("想办法让前端知道 数据不合法，存入失败",error)
            # 数据库roolback回滚

        # code2 情况二 redis不存在数据，只要往数据库写
    else:
        try:
            add_db = 'REPLACE INTO ascd(NAME, FREQUENCY, MINEAREA)  VALUES(%r,%s,%s)' % (name, frequency, minearea)
            mdb = cursor.execute(add_db)  # 数据库操作返回

            if mdb:
                print('插入mysql成功')
                db.commit()

                data_info = {'name': name,
                             'frequency': frequency,
                             'minearea': minearea}#返回
                r.hset(find_info, mapping = data_info)
                result = r.hgetall(find_info)
                print('创建---',result)
                r.expire(find_info, 600)  # 设置过期时间

        except MySQLError as error:
            all_keys = r.hkeys(find_info)
            r.hdel(find_info, *all_keys)
            db.rollback()
            print("想办法让前端知道 数据不合法，存入失败",error)

    return 'yesyesyes'


if __name__ == '__main__':
    keys=r.keys()
    print(keys)
    # r.delete(*keys)
    # keys = r.keys()
    # print(keys)
    app.run()
