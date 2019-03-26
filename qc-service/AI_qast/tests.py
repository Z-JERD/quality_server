"""

from django.test import TestCase

# Create your tests here.
"""
"""
{
    "condition": "(c10001 && c10004)",
    "siteId": "x888",
    "name": "更新测试",
    "expression": "True",
    "ruleType": 3
}

{
    "data": "r10002",
    "msg": "规则表更新成功: r10002",
    "code": 0
}

{
    "data": "r10004",
    "msg": "规则表删除成功: r10004",
    "code": 0
}

{
    "code": 0,
    # "data": null,
    "msg": "c10001: 条件数据数据创建成功"
}



{
         "operator":"o10004(60) && o10005(0.8)",
         "role_scope": 1,
         "text_scope":"2|5",
         "reference_content":"欢迎你的咨询"
}

{
    "code": 0,
    "msg": "规则c10003: 条件数据更新成功"
    # "data": null,
}


"""

"""

# from django.core.cache import cache
# from django_redis import get_redis_connection
# conn = get_redis_connection("default")
# conn.hget("key","name",'wer')
# conn.expire("key",100) #设置过期时间
# conn.persist("key") #移除过期时间
# conn.ttl("key")  #查看剩余时间



# cache.set("key","name",timeout=1209600)
# cache.hset(id, "0", timeout=1209600)
# conn.set()
# conn.hset()


# data=[
#     {'reference_content': '欢迎你的咨询',
#      'condition_id': 'c10003',
#      'role_scope': 1,
#      'operator': 'o10004(60) && o10005(0.8)',
#      'text_scope': '2|5'
#      }
# ]
# role_scope = data[0].get('role_scope')
# print(role_scope)

# flag = True
# data = [1,2,3,4,5]
# time = 0
# for i in data:
#     print(time)
#     if flag:
#         if i < 4:
#             continue
#     time = i

# import jieba
# import gensim
# from gensim import corpora
# from gensim import models
# from gensim import similarities


# msg = "当前说话时间间隔是%s 秒,未超过最大限制的时间"
# limit_word = '时间|您好'
# msg_list = [word for word in jieba.cut(msg)]
# limit_word_list = [i.strip() for i in limit_word.split('|')]
# word_num = len(limit_word_list)
# result = [i for i in limit_word_list if i in msg_list]
# print(result)
# if result:pass
# else:

"""

#百度接口测试
"""
import json
data = {'reference_content': '欢迎你的咨询',
'condition_id': 'c10003',
'role_scope': 1,
'operator': 'o10004(60) && o10005(0.8)',
'text_scope': '2|5'
}
"""


import  time
# time1= 1533522102762 // 1000
# print(time1)
#
# time_data = time.strftime("%Y-%m-%d  %X",time.localtime(time1 ))
#
# print(time_data)

start = '2018-08-03'  # 1536422400000  #1533657600000 #1533830400000
#
start_time = int(time.mktime(time.strptime(start, "%Y-%m-%d")) *1000)
print(start_time)
start_time = int(time.mktime(time.strptime(start, "%Y-%m-%d")) *1000) + 86400000 #毫秒
print(start_time)
# print(time.strftime("%Y-%m-%d %X",time.localtime(1534323851)))


