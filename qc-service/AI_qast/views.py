# -*-coding: utf-8-*-
import time
import json
import logging
import uuid

from django.shortcuts import render, HttpResponse, redirect

from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.decorators import list_route
from django.db.utils import IntegrityError,OperationalError
from redis.exceptions import ConnectionError

from utils.response import BaseResponse,FieldNullException
from  utils.redisfile import DealRedis
from utils.cassandre_sql import *
from analysis.rulefile import RuleDealTask
from AI_qast.models import QualityRule, Condition, Operator,RulePoint
from AI_qast.serializers import QualityRuleSerializer, ConditionSerializer, OperatorSerializer,  RulePointSerializer
logger = logging.getLogger('all')


class QualityRuleModelView(ModelViewSet):
    queryset = QualityRule.objects.all().filter(is_delete=False)
    serializer_class = QualityRuleSerializer
    redis = DealRedis()
    '''
               {
                   "siteId":"kf_888",
                   "rule_name":"规则测试",
                   "rule_type":1,
                   "rule_description":"这是个测试规则",
                   "attribute":1,
                   "mood_expression":1,
                   "condition":"23ea7b26 && 5237db30",
                   "grade" :20,
                   "is_template":1
                }

       '''
    @staticmethod
    def _format_data(data):
        format_data = {
            'rule_name': data.get('rule_name', ''),
            'rule_type': data.get('rule_type',1),
            'rule_description': data.get('rule_description', ''),
            'attribute':data.get('attribute', 1),
            'mood_expression': data.get('mood_expression',1),
            'condition': data.get('condition'),
            'grade': data.get('grade',''),
            'is_template': data.get('is_template', 0)
        }
        return format_data

    def list(self, request, *args, **kwargs):
        res = BaseResponse()
        Cassandra_obj = CassandraRule()
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
        start_time = time.time()
        _data = request.data
        logger.info('创建规则表数据: %s' %(_data) )
        res = BaseResponse()
        Cassandra_obj = CassandraRule()
        try:
            data = self._format_data(_data)
            ruleId = str(uuid.uuid1()).split('-')[0]
            siteId = _data.get('siteId')
            data.update({'rule_id': ruleId, 'site_id':siteId})
            if not data['condition'] or not siteId :
                raise FieldNullException('条件/站点ID 字段的值不能为空')
            else:
                Cassandra_obj.create_data(data)
        except TypeError as e:
            res.code = 1904
            res.msg = '数据的key有误'
            logger.debug('数据的key有误')
        except FieldNullException as e:
            res.code = 1905
            res.msg = '条件/站点ID字段不能为空'
            logger.debug('规则数据%s的条件/站点ID字段不能为空: %s' % ruleId)
        except OperationalError  as e:
            res.code = 1906
            res.msg = '数据库连接失败'
            logger.debug('数据库连接失败')
        except IntegrityError as e:
            if e.args[0] == 1062:
                res.code = 1907
                res.msg = '规则ID重复'
                logger.debug('规则ID重复')
        except ValueError as e:
            res.code = 1908
            res.msg = '参数错误：%s' % ruleId
            logger.debug('创建规则表数据的参数错误')
        except Exception as e:
            res.code = 1909
            res.msg = '规则表创建失败:%s' % ruleId
            logger.debug('规则表%s创建失败:%s' % (ruleId,e))
        else:
            res.data = ruleId
            res.code = 0
            res.msg = '规则表创建成功: %s' % ruleId
            logger.info('规则表创建成功: %s' % ruleId)
            # 将数据存到redis缓存中
            attribute = data['attribute']
            site_rule_key = '%s_%s_%s' % (siteId,attribute,ruleId)
            try:
                self.redis.join_redis(site_rule_key, data)
            except ConnectionError as e:
                logger.debug('redis连接失败,规则未加入到缓存中: %s' % ruleId)
        finally:
            logger.info('create QualityRule----time:%.5fs' % (time.time() - start_time))
            return Response(res.dict, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        start_time = time.time()
        _data = request.data
        logger.info('更新规则表数据: %s' % (_data))
        res = BaseResponse()
        Cassandra_obj = CassandraRule()
        try:
            data = self._format_data(_data)
            ruleId = kwargs['pk']
            siteId = _data.get('siteId')
            data.update({ 'site_id': siteId,'rule_id': ruleId})
            if not data['condition'] or not siteId:
                raise FieldNullException('条件/站点ID字段的值不能为空')
            else:
                Cassandra_obj.update_data(data, ruleId)
        except TypeError as e:
            res.code = 1904
            res.msg = '数据的key有误'
            logger.debug('数据的key有误')
        except FieldNullException as e:
            res.code = 1905
            res.msg = '条件/站点ID字段不能为空'
            logger.debug('规则数据的条件/站点ID字段不能为空: %s' % ruleId)
        except OperationalError  as e:
            res.code = 1906
            res.msg = '数据库连接失败'
            logger.debug('数据库连接失败')
        except ValueError as e:
            res.code = 1908
            res.msg = '参数错误:%s'  % ruleId
            logger.debug('更新规则表数据的参数错误')
        except Exception as e:
            res.code = 1909
            res.msg = '规则表更新失败: %s' % ruleId
            logger.debug('规则表%s更新失败： %s'% (ruleId,e) )
        else:
            res.data = ruleId
            res.code = 0
            res.msg = '规则表更新成功: %s'  % ruleId
            logger.info('规则表更新成功: %s' % ruleId)

            #更新操作,删除原来ruleId对应的数据,新建更新后的数据
            site_rule_key = '%s_%s_%s' % ('*','*', ruleId)
            try:
                self.redis.find_delete_key(site_rule_key)
                attribute = data['attribute']
                new_site_rule_key = '%s_%s_%s' % (siteId,attribute, ruleId)
                self.redis.join_redis(new_site_rule_key, data)
            except ConnectionError as e:
                logger.debug('redis连接失败,数据未更新到缓存中: %s' % ruleId)
        finally:
            logger.info('update QualityRule----time:%.5fs' % (time.time() - start_time))
            return Response(res.dict, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        start_time = time.time()
        ruleId = kwargs['pk']
        logger.info('删除规则的id: %s' % (ruleId))
        res = BaseResponse()
        Cassandra_obj = CassandraRule()
        try:
            Cassandra_obj.delete_data(ruleId)
        except OperationalError  as e:
            res.code = 1906
            res.msg = '数据库连接失败'
            logger.debug('删除规则数据时数据库连接失败')
        except Exception as e:
            res.code = 1909
            res.msg = '规则删除失败: %s' % ruleId
            logger.debug('规则%s删除失败:%s' % (ruleId,e))
        else:
            res.data = ruleId
            res.code = 0
            res.msg = '规则删除成功: %s' % ruleId
            logger.info('规则删除成功: %s' % ruleId)
            site_rule_key = '%s_%s_%s' % ("*","*", ruleId)
            try:
                self.redis.find_delete_key(site_rule_key)
            except ConnectionError as e:
                logger.debug('redis连接失败,数据从缓存中删除: %s' % ruleId)

        finally:
            logger.info('destroy QualityRule----time:%.5fs' % (time.time() - start_time))
            return Response(res.dict, status=status.HTTP_200_OK)


class ConditionModelView(ModelViewSet):
    queryset =  Condition.objects.all().filter(is_delete=False)
    serializer_class =ConditionSerializer
    redis = DealRedis()

    '''
    {
         "condition_name":"测试时间间隔和关键字",
         "condition_description":"这个条件是测试时间和关键字的的",
         "operator":"op001_60|2 && op002_你好|抱歉&2",
         "text_scope":"4|23",
         "role_scope": 0,
         "reference_content":"我们公司会帮您解决"
    }
    
    '''

    @staticmethod
    def _format_data(data):
        format_data = {
            'condition_name':data.get('condition_name',''),
            'condition_description':data.get('condition_description',''),
            'operator': data.get('operator', ),
            'text_scope': data.get('text_scope', "1|-1"),
            'role_scope': data.get('role_scope',1),
            'reference_content': data.get('reference_content',''),
        }
        return format_data

    def list(self, request, *args, **kwargs):
        res = BaseResponse()
        Cassandra_obj = CassandraCondition()
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
        start_time = time.time()
        _data = request.data
        logging.info('创建条件数据：%s'% (_data))
        res = BaseResponse()
        Cassandra_obj = CassandraCondition()
        try:
            data = self._format_data(_data)
            conditionId = str(uuid.uuid1()).split('-')[0]
            data.update({'condition_id': conditionId})
            if not data['operator']:
                raise FieldNullException('算子字段的值不能为空')
            else:
                Cassandra_obj.create_data(data)
        except TypeError as e:
            res.code = 1904
            res.msg = '数据的key有误'
            logger.debug('数据的key有误')
        except FieldNullException as e:
            res.code = 1905
            res.msg = '算子字段不能为空'
            logger.debug('条件数据%s的算子字段不能为空: %s' % conditionId)
        except OperationalError  as e:
            res.code = 1906
            res.msg = '数据库连接失败'
            logger.debug('数据库连接失败')
        except IntegrityError as e:
            if e.args[0] == 1062:
                res.code = 1907
                res.msg = 'ID重复'
                logger.debug('ID重复')
        except ValueError  as e:
            res.code = 1908
            res.msg = '参数错误: %s' % conditionId
            logger.debug('创建条件数据的参数错误: %s' % conditionId)
        except Exception as e:
            res.code = 1909
            res.msg = '条件数据创建失败: %s' % conditionId
            logger.debug('条件%s数据数据创建失败: %s' % (conditionId,e))
        else:
            res.data = conditionId
            res.code = 0
            res.msg = '%s: 条件数据创建成功' % conditionId
            logger.info('条件数据创建成功: %s' % conditionId)
            # 将数据存到redis缓存中
            try:
                self.redis.join_redis(conditionId, data)
            except ConnectionError as e:
                logger.debug('redis连接失败,数据未加入到缓存中: %s' % conditionId)
        finally:
            logger.info('create Condition----time:%.5fs' % (time.time() - start_time))
            return Response(res.dict, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        start_time = time.time()
        _data = request.data
        logging.info('更新条件数据：%s '% _data)
        res = BaseResponse()
        Cassandra_obj = CassandraCondition()
        try:
            data = self._format_data(_data)
            conditionId = kwargs['pk']
            if not data['operator']:
                raise FieldNullException('算子字段的值不能为空')
            else:
                Cassandra_obj.update_data(data,conditionId)
        except TypeError as e:
            res.code = 1904
            res.msg = '数据的key有误'
            logger.debug('数据的key有误')
        except FieldNullException as e:
            res.code = 1905
            res.msg = '算子字段不能为空'
            logger.debug('条件数据%s的算子字段不能为空: %s' % conditionId)
        except OperationalError  as e:
            res.code = 1906
            res.msg = '数据库连接失败'
            logger.debug('更新条件时数据库连接失败')
        except IntegrityError as e:
            if e.args[0] == 1062:
                res.code = 1907
                res.msg = 'ID重复'
                logger.debug('ID重复')
        except ValueError  as e:
            res.code = 1908
            res.msg = '参数错误: %s' % conditionId
            logger.debug('更新条件数据的参数错误: %s' % conditionId)
        except Exception as e:
            res.code = 1909
            res.msg = '条件数据更新失败: %s' % conditionId
            logger.debug('条件%s数据更新失败: %s' % (conditionId,e))
        else:
            res.code = 0
            res.msg = '%s: 条件数据更新成功' % (conditionId)
            logger.debug('%s: 条件数据更新成功' % (conditionId))
            data.update({'condition_id' :conditionId})
            try:
                self.redis.join_redis(conditionId, data)
            except ConnectionError as e:
                logger.debug('redis连接失败,更新缓存数据失败: %s' % conditionId)
        finally:
            logger.info('create Condition----time:%.5fs' % (time.time() - start_time))
            return Response(res.dict, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        start_time = time.time()
        conditionId = kwargs['pk']
        logger.info('删除条件数据id: %s'  % conditionId)
        res = BaseResponse()
        Cassandra_obj = CassandraCondition()
        try:
            Cassandra_obj.delete_data(conditionId)
        except OperationalError  as e:
            res.code = 1906
            res.msg = '数据库连接失败'
            logger.debug('删除条件时数据库连接失败')
        except Exception as e:
            res.code = 1909
            res.msg = '删除条件数据失败: %s' % conditionId
            logger.debug('删除条件数据%s失败：%s' % (conditionId,e))
        else:
            res.data = conditionId
            res.code = 0
            res.msg = '删除条件成功: %s' % (conditionId)
            logger.info('删除条件成功 :%s' % (conditionId))
            try:
                self.redis.delete_redis(conditionId)
            except ConnectionError as e:
                logger.debug('redis连接失败,条件从缓存中删除失败: %s' % conditionId)
        finally:
            logger.info('destroy Condition----time:%.5fs' % (time.time() - start_time))
            return Response(res.dict, status=status.HTTP_200_OK)


class AnalysisModelView(APIView):
    #conn = get_redis_connection('default')
    def __init__(self):
        self.rule_task_obj = RuleDealTask()
        self.redis =  DealRedis()
        self.cassandra_obj = CassandraRule()

    def deal_with_siteId(self,siteId,attribute):
        """
        [
            {'rule_id': 'r10001', 'condition': 'c10001 && c10002'},
            {'rule_id': 'r10002', 'condition': 'c10001 && c10004'},
            {'rule_id': 'r10003', 'condition': 'c10001 && c10002'}
        ]
        """
        #1.从redis中获取
        site_rule_key = '%s_%s_%s' % (siteId,attribute, '*' )
        data_list, key_not_redis =self.redis.find_get_key(site_rule_key)
        #2.从数据库中获取
        if not (data_list and not key_not_redis):
            # data = QualityRule.objects.filter(site_id=siteId, is_delete=False).values().all()
            # data_list = list(data)
            try:
                data_list = self.cassandra_obj.search(siteId,attribute)
            except Exception as e:
                data_list = []
                logger.debug('从数据库中取规则数据失败：%s' % e)
        return data_list

    def post(self, request):
        res = BaseResponse()
        result_data = []
        converIds = request.data.get('converids')
        siteId = request.data.get('siteid')
        attribute = request.data.get('attribute')
        rule_list = self.deal_with_siteId(siteId,attribute)
        if rule_list:
            logger.info('%s 设置的规则有：%s' % (siteId,rule_list))
            try:
                for conver_data in  converIds:
                    converId = conver_data.get('converid')
                    messages = conver_data.get('messages')
                    current_converId_result = []
                    converId_grade = []
                    for rule_data in rule_list:
                        start_time = time.time()
                        rule_id = rule_data.get('rule_id')
                        rule_deal_result,rule_grade = self.rule_task_obj.deal_rule(rule_data, messages)
                        logger.info('处理规则%s 用的时间是%s' % (rule_id, time.time() - start_time))
                        current_converId_result.append(rule_deal_result)
                        converId_grade.append(rule_grade)
                    grade =sum(converId_grade)
                    converId_grade.clear()
                    result_message = {
                        'converid':converId,
                        'grade':grade,
                        'rule_list': current_converId_result
                    }
                    result_data.append(result_message)
            except Exception as e:
                logger.debug('规则解析失败：%s' % e)
            msg = '质检完成'
            code = 0
        else:
            logger.info('%s没有设置规则' % (siteId))
            msg = '该公司未设定质检规则'
            code = 1000
        
        res.data = result_data
        res.code = code
        res.msg = msg
        return Response(res.dict, status=status.HTTP_200_OK)






