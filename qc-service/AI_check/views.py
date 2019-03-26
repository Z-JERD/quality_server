from django.shortcuts import render
import uuid
import json
import copy
import time
import requests
import logging

from django.shortcuts import render, HttpResponse, redirect

from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import list_route
from django.db.utils import IntegrityError,OperationalError
from redis.exceptions import ConnectionError
from django.shortcuts import render, redirect,HttpResponse

from utils.response import BaseResponse,FieldNullException
from utils.redisfile import DealRedis
from utils.cassandre_sql import *
from AI_qast.models import Task, Conversation,ConversationMessage,RulePoint
from AI_check.serializers import TaskSerializer, ConversationSerializer,MessageSerializer,RulePointSerializer
from AI import settings

from .cassand import get_cassandre_data
logger = logging.getLogger('all')

class QualityTaskModelView(ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    redis = DealRedis()
    '''
           {
               "site_id":"kf_888",
               "task_name":"任务1",
               "start_time":"2018-08-01",
               "end_time":"2018-08-01",
               "monitor_type":1,
               "transaction_id":"qwe234fred"
            }

    '''

    @staticmethod
    def _format_data(data):
        format_data = {
            'site_id': data.get('site_id'),
            'task_name': data.get('task_name'),
            'start_time': data.get('start_time',''),
            'end_time': data.get('end_time',''),
            'monitor_type':data.get('monitor_type',1),
            'transaction_id':data.get('transaction_id',' '),

        }
        return format_data

    def list(self, request, *args, **kwargs):
        res = BaseResponse()
        Cassandra_obj = Cassandratask()
        try:
            data = Cassandra_obj.list()
        except OperationalError  as e:
            res.code = 1906
            res.msg = '数据库连接失败'
            logger.debug('数据库连接失败')
            return Response(res.dict, status=status.HTTP_200_OK)
        except Exception as e:
            res.code = 1909
            res.msg = '数据获取失败'
            logger.debug('数据获取失败:%s' % e )
            return Response(res.dict, status=status.HTTP_200_OK)
        else:
            return Response(data,status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        task_start_time = time.time()
        _data = request.data
        logger.info('质检任务: %s' % (_data))
        res = BaseResponse()
        Cassandra_obj = Cassandratask()
        try:
            data = self._format_data(_data)
            taskId = str(uuid.uuid1()).split('-')[0]
            data.update({'task_id':taskId})
            if  not data['start_time'] and not data['transaction_id'] or not data['site_id'] :
                raise FieldNullException('时间/站点ID 字段的值不能为空')
            else:
                Cassandra_obj.create_data(data)
        except TypeError as e:
                res.code = 1904
                res.msg = '数据的key有误'
                logger.debug('数据的key有误')
        except FieldNullException as e:
            res.code = 1905
            res.msg = '时间/站点ID 字段不能为空'
            logger.debug('任务%s的时间/站点ID 字段字段不能为空: %s' % taskId)
        except OperationalError  as e:
            res.code = 1906
            res.msg = '数据库连接失败'
            logger.debug('数据库连接失败')
        except IntegrityError as e:
            if e.args[0] == 1062:
                res.code = 1907
                res.msg = '任务ID重复'
                logger.debug('任务ID重复')
        except ValueError as e:
            res.code = 1908
            res.msg = '参数错误'
            logger.debug('创建任务数据的参数错误')
        except Exception as e:
            res.code = 1909
            res.msg = '任务创建失败:%s' % taskId
            logger.debug('%s任务创建失败:%s' % (taskId,e))
        else:
            res.data = taskId
            res.code = 0
            res.msg = '任务创建成功: %s' % taskId
            logger.info('任务创建成功: %s' % taskId)
            try:
                self.redis.join_redis(taskId, data)
            except ConnectionError as e:
                logger.debug('redis连接失败,任务未加入到缓存中: %s' % taskId)
        finally:
            logger.info('create QualityTask----time:%.5fs' % (time.time() - task_start_time))
            return Response(res.dict, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        start_time = time.time()
        _data = request.data
        logging.info('更新任务数据：%s ' % _data)
        res = BaseResponse()
        Cassandra_obj = Cassandratask()
        try:
            data = self._format_data(_data)
            taskId = kwargs['pk']
            if not data['start_time'] and not data['transaction_id'] or not data['site_id']:
                raise FieldNullException('时间/站点ID 字段的值不能为空')
            else:
                Cassandra_obj.update_data(data,taskId)
        except FieldNullException as e:
            res.code = 1905
            res.msg = '时间/站点ID 字段不能为空'
            logger.debug('任务%s的时间/站点ID 字段字段不能为空: %s' % taskId)
        except OperationalError  as e:
            res.code = 1906
            res.msg = '数据库连接失败'
            logger.debug('数据库连接失败')
        except IntegrityError as e:
            if e.args[0] == 1062:
                res.code = 1907
                res.msg = '任务ID重复'
                logger.debug('任务ID重复')
        except ValueError:
            res.code = 1908
            res.msg = '参数错误'
            logger.debug('任务数据的参数错误')
        except Exception as e:
            res.code = 1909
            res.msg = '任务更新失败:%s' % taskId
            logger.debug('任务%s更新失败:%s' % (taskId,e))
        else:
            res.code = 0
            res.msg = '任务%s: 数据更新成功' % taskId
            logger.info('任务%s: 数据更新成功' % taskId)
            data.update({'task_id': taskId})
            try:
                self.redis.join_redis(taskId, data)
            except ConnectionError as e:
                logger.debug('redis连接失败,任务未更新到缓存中: %s' % taskId)
        finally:
            logger.info('create Condition----time:%.5fs' % (time.time() - start_time))
            return Response(res.dict, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        start_time = time.time()
        task_id = kwargs['pk']
        logger.info('删除任务id: %s' % task_id)
        res = BaseResponse()
        Cassandra_obj = Cassandratask()
        try:
            Cassandra_obj.delete_data(task_id)
        except OperationalError  as e:
            res.code = 1906
            res.msg = '数据库连接失败'
            logger.debug('数据库连接失败')
        except Exception as e:
            res.code = 1909
            res.msg = '任务删除失败: %s' % task_id
            logger.debug('任务%s删除失败:%s' % (task_id,e))
        else:
            res.data = task_id
            res.code = 0
            res.msg = '任务删除成功: %s' % task_id
            logger.info('任务删除成功: %s' % task_id)
            try:
                self.redis.delete_redis(task_id)
            except ConnectionError as e:
                logger.debug('redis连接失败,任务未从缓存中删去: %s' % taskId)
        finally:
            logger.info('destroy QualityTask----time:%.5fs' % (time.time() - start_time))
        return Response(res.dict, status=status.HTTP_200_OK)

class QualityCheckModelView(APIView):
    '''
    开始质检
    '''

    def __init__(self):
        self.cassandra_data =CassandraGetData()
        self.cassandra_result = CassandraQcResult()

    def request_post(self, request_data):
        url = settings.URL
        headers = {
            'Content-Type': 'application/json',
            'Accept-Charset': 'utf-8',
        }
        analysis_time = time.time()
        response = requests.request('POST', url, data=json.dumps(request_data), headers=headers)
        response_data = response.text
        logger.info('分析会话用时:%s' % (time.time() - analysis_time))
        return response_data

    def deal_analysis_request(self,response_data,qc_converids):
        """
        对分析结果处理,存到数据库中
        """
        response = json.loads(response_data)
        converids = response['data']
        for conver_data in converids:
            converid = conver_data.get('converid')
            grade = conver_data.get('grade','')
            rule_data = conver_data.get('rule_list','')
            ruleids = {}
            for rule_message in rule_data:
                ruleid = rule_message.get('ruleid','')
                hit_rule_message = rule_message.get('hit_rule_message','')
                if hit_rule_message:
                    ruleids.update({ruleid:hit_rule_message})
            ruleids_str = json.dumps(ruleids)
            ruleids.clear()
            qc_value = qc_converids.get(converid,'')
            qc_value.update({'grade':grade,'ruleids':ruleids_str})
        return qc_converids

    def create_result(self,result_list):
        for data in result_list:
            yield data

    def get_conversation_message(self, site_id, converid):
        messages = []
        try:
            sql = 'select messageid,createat,type,msgtype,message from dolphin_conversation_message where siteid = %s AND converid = %s  ALLOW FILTERING '
            data = (site_id, converid,)
            conversation_messages =  self.cassandra_data.get_data(sql, data)
        except Exception as e:
            conversation_messages = []
            logger.debug('获取当前会话的会话消息出错')
        if conversation_messages:
            for message_data in conversation_messages:
                message_dict = {
                    'messageid': message_data.messageid,
                    'createat': message_data.createat,
                    'type': message_data.type,
                    'msgtype': message_data.msgtype,
                    'message': message_data.message,
                }
                messages.append(message_dict)
        return messages

    def qc_data(self,siteid,monitor_type,transaction):
        transaction_dict = {
            'siteid':siteid,
            'monitor_type':monitor_type,
            'transaction_id': transaction.converid,
            'starttime': transaction.starttime,
            'endtime': transaction.endtime,
            'customerid': transaction.customerid,
            'firstsupplierid': transaction.firstsupplierid,
        }
        return transaction_dict

    def deal_session_task(self,siteid,start,end,transaction_id,monitor_type):
        converids = []
        qc_converids = {}
        if start and end:
            # 质检时间范围的会话，工单，呼叫
            start_time = int(time.mktime(time.strptime(start, "%Y-%m-%d")) * 1000)  # 毫秒
            end_time = int(time.mktime(time.strptime(end, "%Y-%m-%d"))) * 1000 + 86400000
            start_get_time = time.time()
            try:
                sql = 'select converid,starttime,endtime,customerid,firstsupplierid from dolphin_conversation where siteid = %s AND  starttime >= %s AND endtime >0 AND endtime <= %s  ALLOW FILTERING '
                data = (siteid, start_time, end_time,)
                result = self.cassandra_data.get_data(sql, data)
            except Exception as e:
                result = []
                logger.debug('获取会话的数据出错')
            logger.info('从cassandra提取会话用时:%s' % (time.time() - start_get_time))
            for conversation in result:
                converid = conversation.converid
                # 获取当前会话的消息数据
                messages = self.get_conversation_message(siteid, converid)
                converid_message = {
                    'converid': converid,
                    'messages': messages
                }
                converids.append(converid_message)
                conversation_dict = self.qc_data(siteid, monitor_type, conversation)
                qc_converids.update({converid: conversation_dict})

        elif transaction_id:
            # 质检单个会话
            start_get_time = time.time()
            try:
                sql = 'select converid,starttime,endtime,customerid,firstsupplierid from dolphin_conversation where siteid = %s AND  converid = %s ALLOW FILTERING '
                data = (siteid, transaction_id)
                result = self.cassandra_data.get_data(sql, data)
            except Exception as e:
                result = []
                logger.debug('获取会话的数据出错')
            logger.info('从cassandra提取会话用时:%s' % (time.time() - start_get_time))
            messages = self.get_conversation_message(siteid, transaction_id)
            converid_message = {
                'converid': transaction_id,
                'messages': messages
            }
            converids.append(converid_message)
            conversation_dict = self.qc_data(siteid, monitor_type, result[0])
            qc_converids.update({transaction_id: conversation_dict})

        return converids, qc_converids

    def deal_work_task(self,siteid,start,end,transaction_id,monitor_type):
        pass

    def deal_call_task(self,siteid,start,end,transaction_id,monitor_type):
        pass

    def get(self, request):
        siteid = request.query_params.get('site_id')
        start = request.query_params.get('start_time','')
        end = request.query_params.get('end_time','')
        monitor_type = request.query_params.get('monitor_type')
        transaction_id = request.query_params.get('transaction_id','')

        monitor_type = int(monitor_type)
        if monitor_type == 1:
            extraction_result, qc_converids = self.deal_session_task(siteid,start,end,transaction_id,monitor_type)
        elif monitor_type == 2:
            # 工单任务
            extraction_result, qc_converids = self.deal_work_task(siteid, start, end, transaction_id, monitor_type)
        elif monitor_type == 3:
            # 呼叫中心任务
            extraction_result, qc_converids = self.deal_call_task(siteid, start, end, transaction_id, monitor_type)

        if not extraction_result:
            logger.debug('数据库中无质检任务数据')
            return Response({'msg': '数据库中无质检任务数据'}, status=status.HTTP_200_OK)
        else:
            logger.info('从数据库中获取数据完毕')

        request_data = {
            'siteid': siteid,
            'attribute':monitor_type,
            'converids': extraction_result
        }
        #调用分析模块
        response_data = self.request_post(request_data)
        #对返回的结果处理，更新数据
        deal_response = self.deal_analysis_request(response_data,qc_converids)
        #将结果存到qc_result表中
        result_list = [qc_data for qc_data in  deal_response.values()]
        return Response(result_list, status=status.HTTP_200_OK)
        try:
            data = '质检完成'
            for result_data in self.create_result(result_list):
                self.cassandra_result.create_data(result_data)
        except Exception as e:
            data = '质检失败'
            logger.debug('质检失败:%s',e)
        return Response({'msg':data}, status=status.HTTP_200_OK)

class CheckRequestModelView(APIView):
    '''
    查看质检结果
    '''
    def __init__(self):
        self.cassandra_data = CassandraQcResult()

    def deal_pointrule(self, conversation_data):
        start_time = conversation_data.starttime // 1000
        end_time = conversation_data.endtime // 1000
        starttime = time.strftime("%Y-%m-%d %X ", time.localtime(start_time))
        endtime = time.strftime("%Y-%m-%d %X ", time.localtime(end_time))

        data = {
            'siteid':conversation_data.siteid,
            'monitor_type':conversation_data.monitor_type,
            'transaction_id': conversation_data.transaction_id,
            'starttime': starttime,
            'endtime': endtime,
            'customerid': conversation_data.customerid,
            'firstsupplierid': conversation_data.firstsupplierid,
            'grade': conversation_data.grade
        }
        ruleids_data = conversation_data.ruleids
        if not ruleids_data:
            ruleids_data = '{}'
        ruleids_dict = json.loads(ruleids_data)
        ruleids = list(ruleids_dict.keys())
        data.update({'ruleids': ruleids})
        return data

    def get(self, request):
        siteid = request.query_params.get('site_id')
        start = request.query_params.get('start_time', '')
        end = request.query_params.get('end_time', '')
        monitor_type = request.query_params.get('monitor_type')
        transaction_id = request.query_params.get('transaction_id', '')

        monitor_type = int(monitor_type)
        if start and end:
            start_time = int(time.mktime(time.strptime(start, "%Y-%m-%d")) * 1000)  # 毫秒
            end_time = int(time.mktime(time.strptime(end, "%Y-%m-%d"))) * 1000 + 86400000
            logger.info('查找%s--%s的分析结果' % (start, end))
            try:
                sql = 'select * from qcresult where siteid = %s AND monitor_type = %s AND  starttime >= %s AND endtime >0 AND endtime <= %s  ALLOW FILTERING '
                data = (siteid, monitor_type,start_time,end_time)
                qcresult_data = self.cassandra_data.get_data(sql, data)
            except Exception as e:
                logger.debug('获取质检结果失败:%s' %e)
                return Response({'msg': '获取质检结果失败'}, status=status.HTTP_200_OK)
        elif transaction_id:
            logger.info('查找%s的质检结果' % (transaction_id))
            try:
                sql = 'select * from qcresult where siteid = %s AND monitor_type = %s AND  transaction_id = %s  ALLOW FILTERING '
                data = (siteid, monitor_type,transaction_id)
                qcresult_data = self.cassandra_data.get_data(sql, data)
            except Exception as e:
                logger.debug('获取质检结果失败:%s' % e)
                return Response({'msg': '获取质检结果失败'}, status=status.HTTP_200_OK)
        data = list(map(self.deal_pointrule, qcresult_data))
        return Response(data, status=status.HTTP_200_OK)

class ResultDetailModelView(APIView):
    """
    查看命中规则的会话信息
    """
    def __init__(self):
        self.cassandra_result = CassandraQcResult()
        self.cassandra_data = CassandraGetData()

    def deal_pointmessage(self,transaction_data,messageids ):
        for message_obj in transaction_data:
            point_rule = False
            messageid = message_obj.messageid
            if messageid in messageids:
                point_rule = True
            data = {
                'messageid':messageid,
                'type': message_obj.type,
                'message': message_obj.message,
                'point_rule' : point_rule
            }
            yield data


    def deal_session_pointrule(self,ruleid, siteid,transaction_id,monitor_type):
        try:
            sql = 'select ruleids from qcresult where siteid = %s AND monitor_type = %s AND  transaction_id = %s  ALLOW FILTERING '
            data = (siteid, monitor_type, transaction_id,)
            qcresult_data = self.cassandra_result.get_data(sql, data)
        except Exception as e:
            logger.debug('获取规则详情失败:%s' % e)
            return Response({'msg': '获取规则详情失败'}, status=status.HTTP_200_OK)
        ruleids_data = qcresult_data[0].ruleids
        ruleids_dict = json.loads(ruleids_data)
        ruleids = list(ruleids_dict.keys())
        messageids = ruleids_dict.get(ruleid, '')

        try:
            sql = 'select messageid,type, message from dolphin_conversation_message where siteid = %s  AND  converid = %s   ALLOW FILTERING '
            data = (siteid, transaction_id,)
            transaction_data = self.cassandra_data.get_data(sql, data)
        except Exception as e:
            logger.debug('获取会话消息失败:%s' % e)
            return Response({'msg': '获取会话消息失败'}, status=status.HTTP_200_OK)

        return messageids,transaction_data

    def deal_work_pointrule(self,ruleid, siteid,transaction_id,monitor_type):
        pass

    def deal_call_pointrule(self,ruleid, siteid,transaction_id,monitor_type):
        pass

    def get(self, request):
        ruleid = request.query_params.get('ruleid')
        siteid = request.query_params.get('site_id')
        monitor_type = request.query_params.get('monitor_type')
        transaction_id = request.query_params.get('transaction_id')
        monitor_type = int(monitor_type)

        if monitor_type == 1:
            messageids, transaction_data = self.deal_session_pointrule(ruleid, siteid,transaction_id,monitor_type)
        elif monitor_type == 2: pass

        elif monitor_type == 3: pass

        rule_detail = []
        for message_obj in self.deal_pointmessage(transaction_data, messageids):
            rule_detail.append(message_obj)
        return Response(rule_detail, status=status.HTTP_200_OK)

