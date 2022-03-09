import pymysql
import redis
from pymysql import MySQLError
import time, datetime


class DatabaseSync:
    def __init__(self):
        # 连接MySQL数据库
        try:
            self.conn = pymysql.connect(host='1.1.1.1', port=3306,
                                        user='root', password='111111',
                                        database='python_mysql_test01', charset='utf8')
        except Exception as error:
            print('连接MySQL出现问题！')
            print('失败原因：', error)
            exit()

        try:
            # 建立redis连接池
            self.conn_pool = redis.ConnectionPool(host='1.1.1.1', port=6379, db=0, decode_responses=True,
                                                  password='111111')
            # 客户端0连接数据库
            self.r0 = redis.StrictRedis(connection_pool=self.conn_pool)
        except Exception as error:
            print('连接redis出现问题！')
            print('失败原因：', error)
            exit()

    # 查询数据
    def get_data(self, stu_id):
        # redis hash表名称
        find_info = 'stu_id:' + str(stu_id)

        # 先查询redis数据库是否存在数据,如果存在数据则返回输出，若不存在则去MySQL中查询，然后再将结果更新到redis中
        result = self.r0.hgetall(find_info)
        # 长度>0 即redis存在查询的信息，直接输出信息,否则redis中不存在，需要查询MySQL
        if len(result) > 0:
            """
            每次在redis中更新或者写入数据都需要设置过期时间10分钟，然后每查询到一次就重置过期时间10分钟，
            若10分钟没有查询到这个数据，就会被清除。这样设置过期时间主要防止redis缓存数据过多，清除不常用缓存数据"""
            self.r0.expire(find_info, 600)
            print(result)
            return result
        else:
            with self.conn.cursor() as cursor:
                try:
                    # 执行MySQL的查询操作
                    cursor.execute('select stu_name, stu_birth, stu_phone from tb_student '
                                   'where stu_id=%s', (stu_id,))
                    result_sql = cursor.fetchall()
                    print(result_sql)

                    # 将查询结果更新写入redis数据库中
                    stu_name, stu_birth, stu_phone = result_sql[0][0], result_sql[0][1], result_sql[0][2]
                    data_info = {'stu_name': stu_name,
                                 'stu_birth': str(stu_birth),
                                 'stu_phone': stu_phone}
                    self.r0.hmset(find_info, data_info)
                    self.r0.expire(find_info, 600)  # 设置过期时间

                    return result_sql
                except Exception as error:
                    print(error)
                finally:
                    self.conn.close()

    """
    更新数据的操作，为了避免更新MySQL后，redis没更新的这一段空挡时间的查询，所以先更新redis，
    再更新MySQL，然后MySQL成功提交后，再次对redis进行重新更新
    """

    def post_data(self):
        # 插入数据
        stu_id, stu_name, stu_birth, stu_phone = 1004, 'Tom', '1993-07-04', '19909092332'
        # redis hash表名称
        find_info = 'stu_id:' + str(stu_id)

        # 先查询redis数据库是否存在数据,如果存在数据则更新redis，再更新MySQL，若不存在则去MySQL中更新,提交成功再次更新redis
        result = self.r0.hgetall(find_info)
        # reids存在数据，则需要对数据进行更新，即先清除再写入; 写入redis后，再将数据写入MySQL
        if len(result) > 0:
            # 清除数据
            all_keys = self.r0.hkeys(find_info)
            self.r0.hdel(find_info, *all_keys)
            data_info = {'stu_name': stu_name,
                         'stu_birth': stu_birth,
                         'stu_phone': stu_phone}
            self.r0.hmset(find_info, data_info)
            self.r0.expire(find_info, 600)  # 设置过期时间

            with self.conn.cursor() as cursor:
                try:
                    # 插入SQL语句，result为返回的结果
                    res_info = cursor.execute(
                        'insert into tb_student values (%s, %s, %s, %s)', (stu_id, stu_name, stu_birth, stu_phone,)
                    )
                    # 成功插入后需要提交才能同步在数据库中
                    if isinstance(res_info, int):
                        print('数据更新成功')
                        self.conn.commit()
                        all_keys = self.r0.hkeys(find_info)
                        # 再次更新redis
                        self.r0.hdel(find_info, *all_keys)
                        self.r0.hmset(find_info, data_info)
                        self.r0.expire(find_info, 600)  # 设置过期时间
                except MySQLError as error:
                    # 如果MySQL提交不成功，清除redis数据
                    all_keys = self.r0.hkeys(find_info)
                    self.r0.hdel(find_info, *all_keys)
                    print(error)
                    self.conn.rollback()
                finally:
                    # 操作执行完成后，需要关闭连接
                    self.conn.close()
        else:
            with self.conn.cursor() as cursor:
                try:
                    # 插入SQL语句，result为返回的结果
                    res_info = cursor.execute(
                        'insert into tb_student values (%s, %s, %s, %s)', (stu_id, stu_name, stu_birth, stu_phone,)
                    )
                    # 成功插入后需要提交才能同步在数据库中
                    if isinstance(res_info, int):
                        print('数据更新成功')
                        self.conn.commit()
                except MySQLError as error:
                    print(error)
                    self.conn.rollback()
                finally:
                    # 操作执行完成后，需要关闭连接
                    self.conn.close()


if __name__ == '__main__':
    dbs = DatabaseSync()
    # dbs.get_data(1003)

    dbs.post_data()
