#算子解析
import logging
import jieba
import  json
import re
from aip import AipNlp
from AI import settings
from django_redis import get_redis_connection

from AI_qast.models import QualityRule, Condition, Operator
from utils.response import  OperatorResponse,AIPException
from  utils.redisfile import DealRedis
from utils.cassandre_sql import *
logger = logging.getLogger('all')

class OperatorTask(object):

    def __init__(self):
        self.InterVal = 1
        self.Keyword = 2
        self.IsQuestion = 3
        self.Similarity = 4
        self.Emotion = 5
        self.RegularMatch = 6
        self.Speed = 7
        self.Turnover = 8
        self.client = AipNlp(settings.APP_ID, settings.API_KEY, settings.SECRET_KEY)
        self.redis = DealRedis()
        self.cassandra_obj = CassandraOperator()

    def deal_operator_InterVal(self,current_message, operator_limit):
        # 时间间隔处理 '60|1'
        limit_list = [i.strip() for i in operator_limit.split('|')]
        limit_time, limit_role = int(limit_list[0]), int(limit_list[1])
        message_time = current_message.get('createat')
        messageId = current_message.get('messageid')
        ret = {'messageid': messageId}
        limit_time *=  1000
        # 相同角色
        if limit_role == 1:
            last_time = current_message.get('last_time')
            time_difference = int(message_time) - int(last_time)
            if time_difference == int(message_time):
                result = True
                msg = "该会话消息是首次发起,查询同一角色之间的对话间隔时间,未超过最大限制的时间 %s 。" % (limit_time)
            elif ime_difference > 0 and time_difference <= limit_time:
                result = True
                msg = "查询同一角色之间的对话间隔时间。说话时间间隔是%s 秒,未超过最大限制的时间 %s 。" % (time_difference, limit_time)
            else:
                result = False
                msg = "查询同一角色之间的对话间隔时间。说话时间间隔是%s 秒,超过最大限制的时间 %s 。" % (time_difference, limit_time)

        # 不同角色
        elif int(limit_role) == 2:
            last_time = current_message.get('different_last_time')
            time_difference = int(message_time) - int(last_time)
            if time_difference == int(message_time):
                result = True
                msg = "该会话消息是首次发起,查询不同角色之间的对话间隔时间，未超过最大限制的时间 %s 。" % (limit_time)

            elif time_difference > 0 and time_difference <= limit_time:
                result = True
                msg = "查询不同角色之间的对话间隔时间。说话时间间隔是%s 秒,未超过最大限制的时间 %s 。" % (time_difference, limit_time)
            else:
                result = False
                msg = "查询不同角色之间的对话间隔时间。说话时间间隔是%s 秒,超过最大限制的时间 %s 。" % (time_difference, limit_time)
        ret.update({"result": result, "msg": msg})
        return ret

    def deal_operator_Keyword(self,current_message, operator_limit):
        # 关键字处理 '你好|您好&1'
        limit_list = [i.strip() for i in operator_limit.split('&')]
        limit_word, limit_type = limit_list[0], int(limit_list[1])

        message = current_message.get('new_message')
        messageId = current_message.get('messageid')
        ret = {'messageid': messageId}

        msg_list = [word for word in jieba.cut(message)]
        limit_word_list = [i.strip() for i in limit_word.split('|')]
        word_num = len(limit_word_list)
        result_list = [i for i in limit_word_list if i in msg_list]

        # 关键字全部出现
        if limit_type == 1:
            if len(result_list) == word_num:
                result = True
                msg = "全部命中关键词 "
            elif result_list:
                result = False
                msg = "只命中关键词%s " % result_list
            else:
                result = False
                msg = "未命中关键词 "

        elif limit_type == 2:
            if result_list:
                result = True
                msg = "命中关键词%s " % result_list
            else:
                result = False
                msg = "该消息未命中关键词 "
        ret.update({"result": result, "msg": msg})
        return ret

    def deal_operator_IsQuestion(self,current_message, operator_limit):
        # 是否是疑问句处理
        message = current_message.get('new_message')
        messageId = current_message.get('messageid')
        ret = {'messageid': messageId}

        msg_list = [word for word in jieba.cut(message)]
        result = [i for i in msg_list if i in settings.Interrogative_library]
        if result:
            result = True
            msg = "该会话消息是疑问句 "
        else:
            result = False
            msg = "该会话消息不是疑问句 "
        ret.update({"result": result, "msg": msg})
        return ret

    def deal_operator_Similarity(self,current_message, operator_limit, reference_content):
        # "0.8"
        # 短文本相似度分析
        new_message = current_message.get('new_message')
        messageId = current_message.get('messageid')
        ret = {'messageid': messageId}
        try:
            text_score = self.client.simnet(reference_content, new_message).get("score")
            if not text_score:
                text_score = 0.0
                raise AIPException('调用百度文本相似度接口出错')
        except AIPException as e:
            logger.debug('调用百度文本相似度接口出错/')
        if  float(text_score) >= float(operator_limit):
           result = True
           msg = "文本相似度为%s 高于设置值 " % text_score
        else:
           result = False
           msg = "文本相似度为%s 低于设置值 " % text_score
        ret.update({"result": result, "msg": msg})
        return ret

    def deal_operator_Emotion(self,current_message, operator_limit):
        # 积极,消极类别 ‘0.6|1'  1：积极的概率 2：消极的概率
        new_message = current_message.get('new_message')
        messageId = current_message.get('messageid')
        ret = {'messageid': messageId}

        limit_list = [i.strip() for i in operator_limit.split('|')]
        limit_value, limit_type = float(limit_list[0]), int(limit_list[1])
        if limit_type == 1:
            try:
                positive = self.client.sentimentClassify(new_message)['items'][0].get('positive_prob')
            except KeyError as e:
                positive = 0
                logger.debug('连接百度情感分析接口出错')
            if positive >= limit_value:
                result = True
                msg = "该消息积极的概率是 %s 高于设置值 " % positive
            else:
                result = False
                msg = "该消息积极的概率是 %s 低于设置值 " % positive
        elif limit_type == 2:
            try:
                negative = self.client.sentimentClassify(new_message)['items'][0].get('negative_prob')
            except KeyError as e:
                negative = 0
                logger.debug('连接百度情感分析接口出错')
            if negative >= limit_value:
                result = True
                msg = "该消息消极的概率是 %s 高于设置值 "  % negative
            else:
                result = False
                msg = "该消息消极的概率是 %s 低于设置值 " % negative
        ret.update({"result": result, "msg": msg})
        return ret

    def deal_regular_match(self,current_message, operator_limit):
        #正则匹配
        new_message = current_message.get('new_message')
        messageId = current_message.get('messageid')
        ret = {'messageid': messageId}
        match = re.search(operator_limit, new_message)
        if match:
            match_words = match.group()
            result = True
            msg = '匹配到：%s' % match_words
        else:
            result = False
            msg = '未匹配到值'
        ret.update({"result": result, "msg": msg})
        return ret

    def deal_speed_monitoring(self,current_message, operator_limit):
        #语速监测
        new_message = current_message.get('new_message')
        messageId = current_message.get('messageid')
        endtime = current_message.get('endtime')
        starttime = current_message.get('starttime')
        ret = {'messageid': messageId}

        time_difference = (endtime - starttime) // 1000  #秒
        message_words_num = len(new_message)
        minute_words = round((message_num / time) * 60)
        if minute_words <= operator_limit:
            result = True
            msg = '语速为每分钟%s个字,未超过设置值' % minute_words
        else:
            result = False
            msg = '语速为每分钟%s个字,超过了设置值' % minute_words
        ret.update({"result": result, "msg": msg})
        return ret

    def deal_turnover_interval(self,current_message, operator_limit):
        #工单流传时间间隔
        messageId = current_message.get('messageid')
        time_list= current_message.get('time_list')
        ret = {'messageid': messageId}
        order_time_list = sorted(time_list)
        maximum_time = order_time_list[-1] - order_time_list[0] #毫秒
        maxminute = operator_limit * 6000
        if maximum_time <= maxminute:
            result = True
            msg = '工单流转间隔未超过设置值'
        else:
            result = False
            msg = '工单流转间隔超过了设置值' % minute_words
        ret.update({"result": result, "msg": msg})
        return ret


    def deal_operator_type(self,logical_operator, operator_data, current_message, reference_content):
        """
        ! 'o10004_60|1'
        """
        messageid = current_message.get('messageid', '')
        ret = {'messageid': messageid, "result": False, 'msg': ''}
        try:
            if '_' in operator_data:
                operator_data_list = operator_data.split('_')
                operator_list = [i.strip() for i in operator_data_list]
                operatorId, operator_limit = operator_list[0], operator_list[1]
            else:
                operatorId, operator_limit = operator_data, ''
            data = self.redis.get_redis(operatorId)
            if data == operatorId:
                #data = Operator.objects.filter(operation_id=operatorId, is_delete=False).values('operator_type').first()
                try:
                    data = self.cassandra_obj.search(operatorId)
                except Exception as e:
                    data = {}
                    logger.debug('从数据库中取算子数据失败：%s' % e)
                self.redis.join_redis(operatorId, data)
            #测试data = {'type': 1}
            operator_type = data.get('operator_type','')
            #logger.info('当前处理的算子是%s,限制条件是 %s,当前会话id是%s' % (operatorId, operator_limit,messageid))
            if operator_type == self.InterVal:
                ret = self.deal_operator_InterVal(current_message, operator_limit)
            elif operator_type == self.Keyword:
                ret = self.deal_operator_Keyword(current_message, operator_limit)
            elif operator_type == self.IsQuestion:
                ret = self.deal_operator_IsQuestion(current_message, operator_limit)
            elif operator_type == self.Similarity:
                ret = self.deal_operator_Similarity(current_message, operator_limit, reference_content)
            elif operator_type == self.Emotion:
                ret = self.deal_operator_Emotion(current_message, operator_limit)
            elif operator_type == self.RegularMatch:
                ret = self.deal_regular_match(current_message, operator_limit)
            elif operator_type == self.Speed:
                ret = self.deal_speed_monitoring(current_message, operator_limit)
            elif operator_type == self.Turnover:
                ret = self.deal_turnover_interval(current_message, operator_limit)
            if logical_operator == '!':
                """
                if not ret['result']:
                    ret.update({'result': True,'logical_operator':logical_operator})
                else:
                    ret.update({'result': False,'logical_operator':logical_operator})
                """
                msg = ret['msg']
                msg += ' 对该算子结果取反 '
                result = ret['result']
                ret.update({'result': not result, 'msg': msg, 'logical_operator':logical_operator})
            #{'result': False,  'data': None, 'logical_operator': '!', 'msg': '该消息消极的概率是 0.692382 高于设置值'}

        except Exception as e:
            logger.debug('算子解析失败：%s' % e)
        return ret



if __name__ == '__main__':
    InterValData ='o10001_60|1'
    KeywordData = 'o10002_你好|内容&2'
    IsQuestionData = 'o10003'
    SimilarityData = 'o10004_0.6'
    EmotionData = 'o10005_0.6|2'
    current_message = {
        "messageid": "m1001",
        "fromuser": "c1001",
        "createat": 12345,
        "type": 1,
        "message": "这是个消息内容。规则是由逻辑运算符和条件组成的表达式，检测当前句子是否是疑问句。服务规范类指一些礼貌用语等，如第一句话必须是您好。",
        "new_message": "这是个消息内容。规则是由逻辑运算符和条件组成的表达式，检测当前句子是否是疑问句。",
        #"new_message":"这是个消息内容。内容是什么",
        #"new_message":"麻烦死了",
        "last_time": 12340,
        "different_last_time":12223
    }
    task_obj = OperatorTask()
    logical_operator = "!"
    reference_content = "消息内容"
    #1.测试说话时间间隔
    ret = task_obj.deal_operator_type(logical_operator, InterValData, current_message, reference_content)
    #2.测试关键字
    #ret = task_obj.deal_operator_type(logical_operator, KeywordData, current_message, reference_content)
    #3.测试疑问句
    #ret = task_obj.deal_operator_type(logical_operator, IsQuestionData, current_message, reference_content)
    #4.测试相似度
    #ret = task_obj.deal_operator_type(logical_operator, SimilarityData , current_message, reference_content)
    #5.测试情绪
    #ret = task_obj.deal_operator_type(logical_operator, EmotionData, current_message, reference_content)
    #print(ret)

