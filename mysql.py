from pymysql import MySQLError
import pymysql
import  pymysql.cursors

class DB():
    # 构造函数
    def __init__(self, host='127.0.0.1', user='root',
                 pwd='123456', db='minecraft1'):
        self.host = host
        self.user = user
        self.pwd = pwd
        self.db = db
        self.conn = None
        self.cur = None

    # 连接数据库
    def connectDatabase(self):
        try:
            self.conn = pymysql.connect(host=self.host,
                                        user=self.user,
                                        password=self.pwd,
                                        database=self.db,
                                        charset='utf8')
        except MySQLError as error:
            print("数据库连接失败",error)
            return False
        self.cur = self.conn.cursor()
        return True

    # 关闭数据库
    def close(self):
        # 如果数据打开，则关闭；否则没有操作
        if self.conn and self.cur:
            self.cur.close()
            self.conn.close()
        return True

    # 执行数据库的sq语句,主要用来做插入操作
    def execute(self, sql, params=None):
        # 连接数据库
        self.connectDatabase()
        try:
            if self.conn and self.cur:
                # 正常逻辑，执行sql，提交操作
                flag = self.cur.execute(sql, params)
                self.conn.commit()
        except MySQLError as error:
            print("execute failed: " + sql)
            print("params: " + params,error)
            self.close()
            return False
        return flag

    # 用来查询表数据
    def fetchall(self, sql, params=None):
        self.execute(sql, params)
        return self.cur.fetchall()

    def fetchone(self, sql, params=None):
        self.execute(sql, params)
        return self.cur.fetchone()

if __name__ == '__main__':
    dbhelper = DB()
    # 创建数据库的表
    sql = "create table maoyan('id'varchar(8),\
            'title'varchar(50),\
            'star'varchar(200), \
            'time'varchar(100),primary key('id'));"
    result = dbhelper.execute(sql,None)
    if result:
        print("maoyan　table创建成功")
    else:
        print("maoyan　table创建失败")
