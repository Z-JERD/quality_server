from django.shortcuts import render, HttpResponse, redirect
from AI_qast.models import QualityRule, Condition,  Task, Conversation,ConversationMessage,RulePoint
import requests
import json
import time
import uuid
URL = "http://127.0.0.1:8000/api/v1"
def rule_list(request):
    rule_obj = QualityRule.objects.all().filter(is_delete=False)
    return render(request, 'rule_list.html', {'rule_list': rule_obj })
def rule_add(request):
    if request.method == 'POST':
        siteId = request.POST.get("siteId")
        ruleId = request.POST.get('ruleId')
        name = request.POST.get("name")
        ruleType = request.POST.get("ruleType")
        description = request.POST.get("description")
        grade = request.POST.get("grade")
        operator = request.POST.get("operator")
        conditions = request.POST.getlist("condition")
        condition_operator = conditions[0]+operator+ conditions[1]

        data = {
            'siteId': siteId,
            'name': name,
            'rule_type':int(ruleType),
            'rule_description':description,
            'condition': condition_operator,
            'grade':int(grade),
        }
        url = URL + "/quality_rule/"
        headers = {
            'Content-Type': "application/json",
            'Accept-Charset': "utf-8",
        }
        response = requests.request("POST", url, data=json.dumps(data), headers=headers)

        return redirect('/rule_list/')
def rule_del(request):
    ruleId = request.GET.get('ruleId')
    url = URL + "/quality_rule/" + ruleId + "/"
    headers = {
        'Content-Type': "application/json",
        'Accept-Charset': "utf-8",
    }
    response = requests.request("DELETE", url, headers=headers)
    return redirect('/rule_list/')

def condition_list(request):
    Condition_obj = Condition.objects.all().filter(is_delete=False)
    return render(request, 'Condition_list.html', {'condition_list': Condition_obj })
def condition_add(request):
    if request.method == 'POST':
        conditionId = request.POST.get("conditionId")
        operators = request.POST.getlist("operator")
        reference_content = request.POST.get('reference_content')
        Logic_operator = request.POST.get("Logic_operator")
        text_scope = request.POST.get("text_scope")
        role_scope = request.POST.get("role_scope")



        InterVal =  request.POST.get("InterVal")
        role = request.POST.get("role",'2')
        is_show = request.POST.get("is_show")
        Keyword = request.POST.get("Keyword")
        Similarity = request.POST.get("Similarity")
        is_positive = request.POST.get("is_positive")
        Emotion = request.POST.get("Emotion")
        operator_list = []
        for  operator in  operators:
            if operator == 'o10001':
                operator = operator + '_' + InterVal + '|' + role
            elif operator == 'o10002':
                operator = operator + '_' + Keyword + '&' + is_show
            elif operator == 'o10004':
                operator = operator + '_' + Similarity
            elif operator == 'o10005':
                operator = operator + '_' + Emotion  + '|' + is_positive
            operator_list.append(operator)

        operator = operator_list[0] + ' '+ Logic_operator + ' ' + operator_list[1]
        data = {
            'operator': operator,
            'text_scope': text_scope,
            'role_scope': int(role_scope),
            'reference_content': reference_content,

        }

    url = URL+ "/condition/"
    headers = {
        'Content-Type': "application/json",
        'Accept-Charset': "utf-8",
    }
    response = requests.request("POST", url, data=json.dumps(data), headers=headers)

    return redirect('/condition_list/')
def condition_del(request):
    conditionId = request.GET.get('conditionId')
    url = URL + "/condition/" + conditionId + "/"
    headers = {
        'Content-Type': "application/json",
        'Accept-Charset': "utf-8",
    }
    response = requests.request("DELETE", url, headers=headers)
    return redirect('/condition_list/')


def task_list(request):

    task_obj = Task.objects.all().filter(is_delete=False)
    return render(request, 'task_list.html', {'task_list' : task_obj})

def add_task(request):

    if request.method=='POST':
        taskId = str(uuid.uuid1()).split('-')[0]
        site_id=request.POST.get("siteid")
        name = request.POST.get('task_name')
        start_time = request.POST.get("start_time")
        end_time = request.POST.get("end_time")
        Task.objects.create(task_id=taskId,site_id=site_id, name=name,start_time= start_time,end_time = end_time )
        return redirect("/check_list/")

    return render(request,"task_list.html")

def delete_task(request):
    task_id=request.GET.get('task_id',None)
    Task.objects.filter(task_id=task_id).delete()
    return redirect("/check_list/")



#查看质检结果
def deal_pointrule( conversation_data):

    start_time = conversation_data.starttime // 1000
    end_time = conversation_data.endtime // 1000

    starttime = time.strftime("%Y-%m-%d %X ", time.localtime(start_time))
    endtime = time.strftime("%Y-%m-%d %X ", time.localtime(end_time))

    data = {
        'converid': conversation_data.converid,
        'starttime':  starttime,
        'endtime': endtime,
        'customerid': conversation_data.customerid,
        'firstsupplierid': conversation_data.firstsupplierid,
        'grade': conversation_data.grade
    }

    pointrules = conversation_data.pointrules
    if not pointrules:
        pointrules = '[]'
    pointrules_data = json.loads(pointrules)
    data.update({'pointrules': pointrules_data})
    return data

def checkrequest(request):

    siteid = request.GET.get("site_id")
    start = request.GET.get("start_time")
    end = request.GET.get("end_time")
    start_time = time.mktime(time.strptime(start, "%Y-%m-%d")) *1000 #毫秒
    end_time = time.mktime(time.strptime(end, "%Y-%m-%d")) *1000 +86400000
    # start_time = 1533286799243
    # end_time = 1533295992060
    conversations = list(Conversation.objects.filter(siteid=siteid, starttime__gte=start_time,
                                                     endtime__lte=end_time).distinct().order_by('starttime'))

    data = list(map(deal_pointrule, conversations))

    return render(request, "result.html",{'result_obj':data})

#查看命中的规则详情
def deal_pointmessage(message_obj,messageids ):
    point_rule = False
    messageid = message_obj['messageid']
    if messageid in messageids:
        point_rule = True
    data = {
        'type': message_obj['type'],
        'message': message_obj['message'],
        'point_rule' : point_rule
    }
    return data

def sationrule(request):
    ruleid = request.GET.get('ruleid')
    conveid = request.GET.get('converid')
    description = QualityRule.objects.filter(rule_id=ruleid).values('rule_description').first()
    point_messages = RulePoint.objects.filter(conveid=conveid, ruleid=ruleid).values('messageid').first()
    messageids = json.loads(point_messages["messageid"])
    all_message = list(
        ConversationMessage.objects.filter(conveid=conveid).order_by('createat').values('messageid', 'type', 'message'))
    data = []

    for message_obj in all_message:
        message = deal_pointmessage(message_obj, messageids)
        data.append(message)
    return render(request, "rule_deatil.html", {'message_obj': data,'rule_description':description['rule_description']})

