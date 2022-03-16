import requests

# #接口1：上传ASC文件
# file_data = {'file': open(r'd:/01.asc', 'rb')}
# user_info = {'frequency': 25565,'minearea':'1'}
# r = requests.post("http://127.0.0.1:5000/upload/asc", data=user_info, files=file_data)
# print(r.text)

# #接口2：标注波形
# filename = '01.asc'
# r = requests.get("http://127.0.0.1:5000/phasepick/%s"%filename)
# print(r.text)
#
# #接口3：获取波形文件列表
# requests.get("http://127.0.0.1:5000/wavefile_list")
#
# #接口4：震源定位
# filenames  = ['01.asc','02.asc']
# r = requests.post("http://127.0.0.1:5000/locate",data=filenames)
# print(r.text)
#
# #接口5：获取震源列表
# minearea = '2'
# r = requests.get("http://127.0.0.1:5000/rockburst_location_list",data=minearea)
# print(r.text)

#接口6：上传dxf文件；

# #奇怪的接口：
# da = 'swd'
# requests.post("http://hk4e-sdk.mihoyo.com",data=da)
