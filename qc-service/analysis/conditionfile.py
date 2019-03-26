import logging
import json
from django_redis import get_redis_connection
from AI_qast.models import QualityRule, Condition, Operator
from analysis.operatorfile import OperatorTask
from  utils.redisfile import DealRedis
from utils.cassandre_sql import *

logger = logging.getLogger('all')


class ConditionTask(object):
    #解析单个条件
    def __init__(self):
        #self.conn = get_redis_connection("default")
        self.deal_task_obj = OperatorTask()
        self.redis = DealRedis()
        self.cassandra_obj = CassandraCondition()

    def deal_operator_list(self,operator_list, current_message, reference_content):
        """
        处理条件中的算子
        operator_list = ['o10004_60|1', 'o10003_你好|您好]
        """
        operator_result = []
        for operator_data in operator_list:
            logical_operator = ''
            if '!' in operator_data:
                logical_operator = '!'
                operator_data = [i.strip() for i in operator_data.split('!')][1]
            result = self.deal_task_obj.deal_operator_type(logical_operator, operator_data, current_message, reference_content)
            # {'result': False, 'grade': 20, 'data': None, 'logical_operator': '!', 'msg': '该消息消极的概率是 0.692382 高于设置值'}
            operator_result.append(result)
        return operator_result

    def deal_operator_result(self, operator_result, condition_operator,logical_operator):
        #对当前会话处理的结果进行整合
        """
           [
               {'messageid': 'm1001', 'result': True, 'msg': '该会话消息是首次发起,未超过最大限制的时间 60', 'grade': 20},
               {'messageid': 'm1001', 'result': False, 'msg': '该会话消息是首次发起,未超过最大限制的时间 40', 'grade': 20, 'logical_operator': '!'}
           ]
        """
        results = []
        for message in operator_result:
            for new_message in results:
                if new_message['messageid'] == message['messageid']:
                    new_message.setdefault('result', []).append(message['result'])
                    new_message.setdefault('msg', []).append(message['msg'])
                    break
            else:
                dic = {}
                dic['messageid'] = message['messageid']
                dic['msg'] = [message['msg']]
                dic['result'] = [message['result']]
                results.append(dic)
        if not results:
            deal_result = {}
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
                result = False
            msg = deal_result['msg']
            msg = " || ".join(msg)
        else:
            result = deal_result['result'][0]
            msg = deal_result['msg'][0]
        deal_result.update({'msg': msg, 'result': result})
        if condition_operator == '!' or condition_operator == '！':
            msg += '对整体结果取反'
            deal_result.update({ 'result': not result, 'msg' : msg})
        #logger.info('算子整合后的结果是：%s' %deal_result )
        return deal_result

    def split_logical_operator(self,data):
        # 逻辑运算符分割
        if '&&' in data:
            data = data.split('&&')
            data_list = [i.strip() for i in data]
            return data_list, '&&'
        elif '||' in data:
            data = data.split('||')
            data_list = [i.strip() for i in data]
            return data_list, '||'

    def deal_text(self, text_scope, messages):
        #处理文本
        text_scope_list = text_scope.split('|')
        text_list = [int(text.strip()) for text in text_scope_list]
        start_num, end_num = text_list[0] - 1, text_list[1]
        if end_num == -1:
            new_messages = messages[start_num:]
        else:
            new_messages = messages[start_num:end_num]

        return new_messages

    def deal_meaasge(self, data, condition_operator, conditionId, messages):
        role_scope = data.get('role_scope',1)
        text_scope = data.get('text_scope','1|-1')
        operator = data.get('operator')
        reference_content = data.get('reference_content', '')
        #logger.info('条件%s对应的算子是%s,查询的角色是%s,查询范围是%s' % (conditionId, operator, role_scope, text_scope))
        last_time = 0  # 相同角色上一消息发送时间
        different_last_time = 0  # 不同角色上一消息发送时间
        new_messages = self.deal_text(text_scope, messages)
        for current_message in new_messages:
            # 1.身份判断
            if role_scope:
                message_type = current_message.get('type',1)
                if not message_type:
                    message_type = 1
                if role_scope != message_type:
                    different_last_time = current_message.get('createat')
                    continue
            new_message = current_message['message']
            current_message.update(
                {"new_message": new_message, "last_time": last_time, "different_last_time": different_last_time})
            # 3.获取算子operator = !'o10004_60|1 && o10005_0.8'
            if '&&' in operator or '||' in operator:
                operator_list, logical_operator = self.split_logical_operator(operator)
            else:
                operator_list, logical_operator = [operator, ], ''
            operator_result = self.deal_operator_list(operator_list, current_message, reference_content)
            deal_result = self.deal_operator_result(operator_result, condition_operator, logical_operator)
            last_time = current_message.get('createat')
            yield  deal_result


    def deal_condition(self ,condition_operator, conditionId, messages):
        # 解析单个条件 '!c10002'
        #1.从缓存中取到数据 2.从数据库中获取数据
        deal_condition_result = []
        data  = self.redis.get_redis(conditionId)
        if data == conditionId:
            # data = Condition.objects.filter(condition_id=conditionId, is_delete=False).values().first()
            # data.pop('created_at')
            # data.pop('updated_at')
            try:
                data = self.cassandra_obj.search(conditionId)
            except Exception as e:
                data = {}
                logger.debug('从数据库中取条件数据失败：%s' % e)
            self.redis.join_redis(conditionId, data)
        if data:
            operator = data.get('operator')
            for deal_result in self.deal_meaasge(data, condition_operator, conditionId, messages):
                deal_condition_result.append(deal_result)
            logger.info('---------->当前条件%s 对应的组合算子%s  对每条会话消息的处理结果集是%s' % (conditionId, operator, deal_condition_result))
        return  deal_condition_result

