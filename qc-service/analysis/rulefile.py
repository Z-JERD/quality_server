import time
import logging
from analysis.conditionfile import  ConditionTask

logger = logging.getLogger('all')

class RuleDealTask(object):

    def __init__(self):
        self.condition_task = ConditionTask()

    def deal_conditions_result(self,ruleId,conditions_result, logical_operator,condition_num):
        content_result = []
        has_hit_rule = []
        no_hit_rule = []
        for conditions in conditions_result:
            for condition in conditions:
                content_result.append(condition)
        result_list = []
        for message in content_result:
            for new_message in  result_list:
                if new_message['messageid'] == message['messageid']:
                    new_message.setdefault('result', []).append(message['result'])
                    new_message.setdefault('msg', []).append(message['msg'])
                    break
            else:
                dic = {}
                dic['messageid'] = message['messageid']
                dic['msg'] = [message['msg']]
                dic['result'] = [message['result']]
                result_list.append(dic)
        for current in  result_list:
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
                    result = False
                msg = current['msg']
                msg = " || ".join(msg)
            else:
                result = current['result'][0]
                msg = current['msg'][0]
            current.update({'msg': msg, 'result': result})
            if result == True:
                has_hit_rule.append(current["messageid"])
            else:
                no_hit_rule.append(current["messageid"])
        logger.info('-------****当前规则:%s 对每条会话消息的处理结果：%s' % (ruleId, result_list))
        return has_hit_rule, no_hit_rule


    def deal_condition_list(self ,condition_list, messages):
        # 处理条件前的！ ['c10001', '!c10002']
        deal_condition_result = []
        for conditionId in condition_list:
            start_time = time.time()
            condition_operator = ''
            if '!' in conditionId:
                condition_operator = '!'
                conditionId = [i.strip() for i in conditionId.split('!')][1]

            elif '！' in conditionId:
                condition_operator = '！'
                conditionId = [i.strip() for i in conditionId.split('！')][1]
            result = self.condition_task.deal_condition(condition_operator, conditionId, messages)
            #logger.info('处理条件%s用时：%s' % (conditionId, time.time() - start_time))
            deal_condition_result.append(result)
        return deal_condition_result

    def split_logical_operator(self, data):
        # 逻辑运算符分割
        if '&&' in data:
            data = data.split('&&')
            data_list = [i.strip() for i in data]
            return data_list, '&&'
        elif '||' in data:
            data = data.split('||')
            data_list = [i.strip() for i in data]
            return data_list, '||'
        else:
            return [data,],''

    def deal_rule(self, rule_data, messages):
        """
        获取单条规则对应的所有条件和逻辑运算符
        {'rule_id': 'r10001', 'condition': 'c10001 && c10002'}
        """
        ruleId = rule_data['rule_id']
        rule_condition = rule_data['condition']
        grade = rule_data['grade']
        expression = rule_data['mood_expression']
        The_rule_grade = 0
        has_hit_rule = []
        try:
            if '&&' in rule_condition or '||' in rule_condition:
                condition_list, logical_operator = self.split_logical_operator(rule_condition)
            else:
                condition_list, logical_operator = [rule_condition, ], ''
            # condition_list   ['c10001','!c10002'] logical_operator = &&
            condition_num = len(condition_list)
            logger.info('开始处理规则%s,对应的条件是%s,逻辑运算符是%s' % (ruleId, condition_list, logical_operator))
            conditions_result = self.deal_condition_list(condition_list, messages)

            #使用logical_operator 对结果集进行处理
            has_hit_rule, no_hit_rule = self.deal_conditions_result(ruleId,conditions_result, logical_operator, condition_num)
            if has_hit_rule and expression == 1:
                The_rule_grade = grade
            elif has_hit_rule and expression == 0:
                The_rule_grade = 0 - grade
            elif not has_hit_rule:
                The_rule_grade = 0
        except Exception as e:
            logger.debug('条件解析失败：%s' % e)

        current_rule_data = {
            'ruleid' : ruleId,
            #'rule_get_grade': The_rule_grade,
            'hit_rule_message' : has_hit_rule,
        }
        return current_rule_data,The_rule_grade


