# -*- coding: utf-8 -*-

from django.db import models
from .common import LogicDeleteModel, TimeMarkModel

SERVICE = 1
OPINION = 2
BUSINESS = 3
OTHER = 4

RULE_TYPE = (
    (SERVICE, '服务规范'),
    (OPINION, '舆情监控'),
    (BUSINESS, '业务类'),
    (OTHER, '其他类')
)


ALL = 0
WORKER =1
VISITOR = 2

ROLE_SCOPE =(
    (ALL,'所有'),
    (WORKER,'客服'),
    (VISITOR,'访客'),
)


InterVal = 1
Keyword = 2
IsQuestion = 3
Similarity = 4
Emotion = 5
RegularMatch = 6
Speed = 7
Turnover = 8

OperatorType = (
    (InterVal ,'说话时间间隔'),
    (Keyword,'关键字'),
    (IsQuestion ,'是否是疑问句'),
    (Similarity,'相似度分数'),
    (Emotion,'积极类别的概率'),
    (RegularMatch,'正则匹配'),
    (Speed,'语速监测'),
    (Turnover,'工单流转间隔'),

)


ALL_TEXT = '1|-1'



class QualityRule(LogicDeleteModel, TimeMarkModel):
    rule_id = models.CharField(primary_key=True, max_length=50, db_index=True, unique=True, verbose_name='库表唯一标识')
    site_id = models.CharField(max_length=50, verbose_name='企业唯一标识')
    name = models.CharField(max_length=50, verbose_name='规则名称',null=True)
    #rule_name = models.CharField(max_length=50, verbose_name='规则名称', null=True)
    rule_type = models.IntegerField(choices=RULE_TYPE, verbose_name='规则类别',default=SERVICE)
    rule_description = models.CharField(max_length=256, verbose_name='规则描述',null=True)
    #1.会话 2.工单 3.呼叫中心
    #attribute = models.IntegerField(verbose_name='规则对应的监测类型',default=1)
    mood_expression = models.SmallIntegerField(default=1, verbose_name='正向负向') #0负向 1 正向
    condition = models.CharField(max_length=50, verbose_name='规则对应的条件')
    grade = models.IntegerField(verbose_name='分数设置')
    is_template = models.SmallIntegerField(default=0, verbose_name='是否是模板')

    class Meta:
        verbose_name_plural = '规则表'

    def __str__(self):
        return self.name



class Condition(LogicDeleteModel, TimeMarkModel):
    condition_id = models.CharField(primary_key=True, max_length=50, db_index=True, unique=True, verbose_name='条件唯一标识')
    name = models.CharField(max_length=50, verbose_name='条件名称', null=True)
    #condition_name = models.CharField(max_length=50, verbose_name='条件名称', null=True)
    condition_description = models.CharField(max_length=50, verbose_name='条件描述', null=True)
    operator = models.CharField(max_length=50, verbose_name='条件对应的算子',null= False )
    text_scope = models.CharField(max_length=50,verbose_name='文本检测范围', default=ALL_TEXT)
    role_scope = models.SmallIntegerField(choices=ROLE_SCOPE, verbose_name='角色检测范围', default=WORKER)
    reference_content = models.CharField(max_length=256, verbose_name='参考语句', null=True)

    class Meta:
        verbose_name_plural = '条件表'

    def __str__(self):
        return self.name


class Operator(LogicDeleteModel, TimeMarkModel):
    operation_id = models.CharField(primary_key=True, max_length=50, db_index=True, unique=True, verbose_name='算子唯一标识')
    operator_type = models.SmallIntegerField(choices=OperatorType, verbose_name='算子类型', default=3)
    name = models.CharField(max_length=50, verbose_name='算子名称',null=True)
    #operator_name = models.CharField(max_length=50, verbose_name='算子名称',null=True)

    class Meta:
        verbose_name_plural = '算子表'

    def __str__(self):
        return self.name

class Task(LogicDeleteModel, TimeMarkModel):
    task_id = models.CharField(primary_key=True, max_length=50, db_index=True, unique=True, verbose_name='任务唯一标识')
    site_id = models.CharField( max_length=50, verbose_name='站点ID')
    name = models.CharField( max_length=50, verbose_name='任务名')
    #task_name = models.CharField( max_length=50, verbose_name='任务名')
    start_time = models.CharField(max_length=50, verbose_name='开始时间',null=True)
    end_time = models.CharField(max_length=50, verbose_name='结束时间',null=True)
    #1.会话 2.工单 3.呼叫中心
    # monitor_type = models.IntegerField(verbose_name='任务类别',default=1)
    # transaction_id = models.CharField( max_length=256, verbose_name='会话/工单/呼叫唯一标识',null=True)

    class Meta:
        verbose_name_plural = '质检任务表'

    def __str__(self):
        return self.name

class QcResult(LogicDeleteModel, TimeMarkModel):
    """
    类型[工单 - 呼叫中心 - 会话], transaction_id(convid, orderid, callid), 访客，客服，开始时间，结束时间，ruleids
    {rule1: {msgid1}, rule2: {msgid1, msgid2}}
    """
    siteid = models.CharField(max_length=256, verbose_name='企业id')
    monitor_type = models.IntegerField(verbose_name='任务类别', default=1)
    transaction_id = models.CharField(max_length=256, verbose_name='会话/工单/呼叫中心id')
    starttime = models.BigIntegerField(verbose_name='开始时间')
    endtime = models.BigIntegerField(verbose_name='结束时间')
    customerid = models.CharField(max_length=256, verbose_name='访客id')
    firstsupplierid = models.CharField(max_length=256, verbose_name='客服id')
    ruleids = models.CharField( max_length=256, verbose_name='命中的所有规则',null=True)
    grade = models.IntegerField(verbose_name='总分', null=True)

class Conversation(models.Model):
    siteid = models.CharField(max_length=256, verbose_name='企业id')
    converid = models.CharField( max_length=256, verbose_name='会话id')
    starttime = models.BigIntegerField(verbose_name='开始时间')
    endtime = models.BigIntegerField(verbose_name='结束时间')
    customerid = models.CharField( max_length=256, verbose_name='访客id')
    firstsupplierid = models.CharField( max_length=256, verbose_name='客服id')
    pointrules = models.CharField( max_length=256, verbose_name='命中的所有规则',null=True)
    grade = models.IntegerField(verbose_name='总分', null=True)

    class Meta:
        verbose_name_plural = '会话表'


class ConversationMessage(models.Model):
    siteid = models.CharField( max_length=256, verbose_name='企业id')
    conveid = models.CharField( max_length=256, verbose_name='会话id')
    messageid = models.CharField( max_length=256, verbose_name='消息id')
    createat = models.BigIntegerField( verbose_name='消息创建时间')
    type = models.IntegerField(verbose_name='成员类型',null=True)
    msgtype = models.IntegerField( verbose_name='消息类型',null=True)
    message = models.CharField( max_length=256, verbose_name='消息内容',null=True)

    class Meta:
        verbose_name_plural = '会话消息表'


class RulePoint(models.Model):
    conveid = models.CharField(max_length=256, verbose_name='会话id',null=True)
    messageid = models.CharField(max_length=256, verbose_name='消息id',null=True)
    ruleid = models.CharField(max_length=256, verbose_name='规则id',null=True)

    class Meta:
        verbose_name_plural = '分析命中规则表'


