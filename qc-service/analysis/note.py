"""
算子处理
1. 说话时间间隔  '算子ID_时间间隔|身份 ' 1：相同角色 2：不同角色
                 'o10001_60|2'
2.关键字       '算子ID_关键字1|关键字2 & 出现设置' 1：关键字全部出现 2:关键字不全部出现
                'o10002_你好|您好&1'
3.是否是疑问句 ’算子ID'  'o10003'

4.短文本相似度分析: '算子ID_相似度的值   'o10004_0.8'

5.情绪分析：’算子ID_概率|类别'  1：积极的概率 2：消极的概率 'o10005_0.6|2'
6. 'op006_你好|您好'  'op006_买.*(ssd盘|普通盘)' 正则表达式
7. 'op007_200'  语速监测 每分钟不超过200字
8. 'op008_5' 工单流传间隔 #最大时间不超过5分钟
"""

#将算子类型存到缓存中
"""
import redis
import json
from AI_qast.models import  Operator
pool = redis.ConnectionPool(host='127.0.0.1', port=6379, db=9)
conn = redis.Redis(connection_pool=pool)
conn.flushall() #清空缓存
# all_data = Operator.objects.filter(is_delete=False).values('operation_id','operator_type')
# for data in list(all_data):
#     operator_type = data['operator_type']
#     operationId = data['operation_id']
#     value = {'operator_type': operator_type}
#     conn_value = json.dumps(value)
#     conn.set(operationId,conn_value, ex=1209600)
"""
# import uuid
# rule_id = str(uuid.uuid1()).split('-')[0]
# print(rule_id,type(rule_id))
#百度接口测试
"""

APP_ID = '14483119'
API_KEY = 'pzaEkMs8UzRyvfRDZAKw5ueP'
SECRET_KEY = 'cr9tKY013cgKt5LpjzS3gPavca4HywLI '
from aip import AipNlp
client = AipNlp(APP_ID, API_KEY, SECRET_KEY)
try:
    text_score = client.simnet('抱歉，我们深感歉意', '不好意思').get("score")
    print(text_score)
except Exception as e:
    print(e)
"""



#规则结果整合 r10001 ----->'c10001 && c10002 && c10003 '
"""
conditions = [
    [
        {
            'result': True,
            'messageid': 'm1001',
            'msg': "(该会话消息是首次发起,查询不同角色之间的对话间隔时间，未超过最大限制的时间 60 。命中关键词['服务']  对该算子结果取反  两者的关系是 ||)"
        },
        {
            'result': False,
            'messageid': 'm1003',
            'msg': "(查询不同角色之间的对话间隔时间。说话时间间隔是112 秒,超过最大限制的时间 60 。命中关键词['产品', '服务']  对该算子结果取反  两者的关系是 ||)"
        }
    ],
    [
        {'result': False,
         'messageid': 'm1001',
         'msg': '(文本相似度为0.5093 低于设置值 该会话消息是疑问句  两者的关系是 &&)'
         },
        {'result': False,
         'messageid': 'm1003',
         'msg': '(文本相似度为0.464008 低于设置值 该会话消息不是疑问句  两者的关系是 &&)'
         }
    ]
]

content_result = [ ]

for i in conditions:
    for j in i:
        content_result.append(j)

result = []
for message in content_result:
    for new_message in result:
        if new_message['messageid'] == message['messageid']:
            new_message.setdefault( 'result',[]).append(message[ 'result'])
            new_message.setdefault('msg', []).append(message['msg'])
            break
    else:
        dic = {}
        dic['messageid'] = message['messageid']
        dic['msg'] = [message['msg']]
        dic[ 'result'] = [message[ 'result']]
        result.append(dic)


has_hit_rule = []
no_hit_rule = []
logical_operator = '&&'
for current in result:
    if logical_operator == '&&':
        if False in current['result']:
            result = False
        else:
            result = True
        msg = current['msg']
        msg = " && ".join(msg)

    elif logical_operator == '||':
        if True in current['result']:
            result = True
        else:
            result =  False
        msg = current['msg']
        msg = " || ".join(msg)
    current.update({'msg':msg, 'result' : result})
    if result == True:
        has_hit_rule.append(current)
    else:
        no_hit_rule.append(current)
print(has_hit_rule, no_hit_rule)

"""

##条件结果整合 10001 ----->'o10004_60|1 && o10005_0.8 &&o10003 '
"""
condition = [
    {'messageid': 'm1001', 'result': True, 'msg': '未超过最大限制的时间',},
    {'messageid': 'm1001', 'result': False, 'msg': '未命中关键字',},
    {'messageid': 'm1001', 'result': True, 'msg': '是疑问句',},
]

results = []
for message in condition:
    for new_message in results:
        if new_message['messageid'] == message['messageid']:
            new_message.setdefault( 'result',[]).append(message[ 'result'])
            new_message.setdefault('msg', []).append(message['msg'])
            break
    else:
        dic = {}
        dic['messageid'] = message['messageid']
        dic['msg'] = [message['msg']]
        dic[ 'result'] = [message[ 'result']]
        results.append(dic)
print(results)

logical_operator = '&&'
condition_operator = ''
deal_result = results[0]
if logical_operator == '&&':
    if False in deal_result['result']:
        result = False
    else:
        result = True
    msg = deal_result['msg']
    msg = " && ".join(msg)

elif logical_operator == '||':
    if True in deal_result['result']:
        result = True
    else:
        result =  False
    msg = deal_result['msg']
    msg = " || ".join(msg)
else:
    result = deal_result['result'][0]
    msg = deal_result['msg'][0]
deal_result.update({'msg':msg, 'result' : result})
print(deal_result)
if condition_operator == '!' or condition_operator == '！':
    msg += '  对整体结果取反'
    deal_result.update({'result': not result, 'msg': msg})
#logger.info('算子处理后的结果是：%s' % deal_result)
print(deal_result)


 result_list = []
        if logical_operator == '&&':
            msg = ''
            for i in operator_result:
                messageid = i['messageid']
                result_list.append(i['result'])
                msg += i['msg']
            if False in result_list:
                result = False
            else:
                result =True

        elif logical_operator == '||':
            msg = ''
            for i in operator_result:
                messageid = i['messageid']
                result_list.append(i['result'])
                msg += i['msg']

            if True in result_list:
                result = True
            else:
                result = False
        else:
            messageid = operator_result[0]['messageid']
            result = operator_result[0]['result']
            msg = operator_result[0]['msg']
        msg = '(%s 两者的关系是 %s)' %(msg, logical_operator)
        deal_result = {
            'messageid': messageid,
            'result': result,
            'msg': msg
        }
        if condition_operator == '!' or condition_operator == '！':
            msg += '对整体结果取反'
            deal_result.update({ 'result': not result, 'msg' : msg})
        logger.info('算子处理后的结果是：%s' %deal_result )
        return deal_result
"""
#质检结果
"""
data =  {
               "siteid":"kf_888",
               "monitor_type":1,
               "transaction_id":"qqqqqqq",
                "starttime":1234567123,
                "endtime":1234543,
                "customerid":'qwer345',
                "firstsupplierid":'qwe123',
                "ruleids":"{'123':[1,2,3]}",
                "grade":20
            }
"""

import  time
start = '2018-11-09  13:11:05'   #1541692800000  1541779200000

start_time = int(time.mktime(time.strptime(start, "%Y-%m-%d %X")) *1000)
print(start_time)
# end_time = int(time.mktime(time.strptime(start, "%Y-%m-%d")) *1000) + 86400000 #毫秒
# print(end_time)
# #秒转换成字符串
time1 = 1541740805000 // 1000
time_data = time.strftime("%Y-%m-%d  %X",time.localtime(time1 ))
print(time_data)

# 2800 2018-11-09  09:20:05   2882 2018-11-09  07:30:05   2865  2018-11-09  13:20:05




