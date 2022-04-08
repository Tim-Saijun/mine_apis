import json
import struct
from socket import *
from threading import Thread


# 先转成json  然后len(j_str)即为字节长度
# 发送  flask使用
def tc(md5):
    # IP = '192.168.137.1'
    # IP = '127.0.0.1'
    IP = '10.4.227.92'
    SERVER_PORT = 500

    BUFLEN = 512

    tcp_client = socket(AF_INET, SOCK_STREAM)

    tcp_client.connect((IP, SERVER_PORT))
    print('连接成功')
    md5_json = json.dumps(md5)
    head_len = struct.pack("i", len(md5_json))
    tcp_client.send(head_len)  # 发送md5的长度
    tcp_client.send(md5_json.encode())  # 发送md5

    # 接收返回值-------------------------------------

    head_len = tcp_client.recv(4)  # 接收头的长度
    head_len = struct.unpack('i', head_len)[0]  # 接收头
    head = tcp_client.recv(head_len)
    head = json.loads(head.decode())

    size = head['pick_p']
    pick_p = tcp_client.recv(size)
    pick_p = json.loads(pick_p.decode())
    print('pick_p', pick_p)

    size = head['pick_s']
    pick_s = tcp_client.recv(size)
    pick_s = json.loads(pick_s.decode())
    print('pick_s', pick_s)

    tcp_client.close()
    return pick_p, pick_s
    # for each in key:
    #     size = head[each]
    #     info = tcp_client.recv(size)
    #     info = json.loads(info.decode())
    #     args.append(info)
    # print('开始接收2')
    #
    # print(dict(zip(key, args)))


def solve(md5):
    thread = Thread(target = tc, args = (md5,))
    thread.setDaemon = True
    thread.start()
    print('继续运行')


if __name__ == '__main__':
    solve('md5')

    # asc_file = [1, 2, 3, 4]
    # frequency = [5, 6, 7, 8, 9, 10]
    # minearea = {"a": '111', "b": '222'}
    # md5 = 'md5'
    # asc_file_json = json.dumps(asc_file)
    # frequency_json = json.dumps(frequency)
    # minearea_json = json.dumps(minearea)
    # md5_json = json.dumps(md5)
    # '''只需要md5，其他的不需要，后期修改'''
    # dic = {
    #     "asc_file": len(asc_file_json),
    #     "frequency": len(frequency_json),
    #     "minearea": len(minearea_json),
    #     "md5": len(md5_json)
    # }
    # thread = Thread(target = tc, args = (dic, md5_json))
    # thread.setDaemon = True
    # thread.start()
    # print('继续运行')
