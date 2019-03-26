# -*-coding: utf-8-*-
import requests
import json
URL = "http://127.0.0.1:8000/api/v1"
TASKURL = "http://127.0.0.1:8000/check"
def test_create_rule(url):
    url = url + "/quality_rule/"
    payload =  {
                   "siteId":"kf_888",
                   "rule_name":"测试",
                   "rule_type":1,
                   "rule_description":"",
                   "attribute":1,
                   "mood_expression":1,
                   "condition":"5237db30",
                   "grade" :10,
                   "is_template":1
                }
    headers = {
        'Content-Type': "application/json",
        'Accept-Charset': "utf-8",
    }
    response = requests.request("POST", url, data=json.dumps(payload), headers=headers)
    print(response.text)

def test_update_rule(url,qualityid):
    url = url + "/quality_rule/" + qualityid + "/"
    payload = {
                   "siteId":"kf_888",
                   "rule_name":"更新测试",
                   "rule_type":1,
                   "rule_description":"用来做更新测试",
                   "attribute":2,
                   "mood_expression":2,
                   "condition":"5237db30",
                   "grade" :20,
                   "is_template":0
                }
    headers = {
        'Content-Type': "application/json",
        'Accept-Charset': "utf-8",
    }
    response = requests.request("PUT", url, data=json.dumps(payload), headers=headers)
    print(response.text)

def test_delete_rule(url,qualityid):
    url =url + "/quality_rule/" + qualityid + "/"
    headers = {
        'Content-Type': "application/json",
        'Accept-Charset': "utf-8",
    }
    response = requests.request("DELETE", url, headers=headers)
    print(response.text)

def test_create_condition(url):
    url = url + "/condition/"
    payload = {
         "condition_name":"测试疑问句",
         "condition_description":"这个条件是疑问句的",
         "operator":"op003",
         "text_scope":"1|-1",
         "role_scope": 1,
         "reference_content":"我们公司会帮您解决"
    }
    headers = {
        'Content-Type': "application/json",
        'Accept-Charset': "utf-8",
    }
    response = requests.request("POST", url, data=json.dumps(payload), headers=headers)
    print(response.text)

def test_update_condition(url,conditionid):
    url = url + "/condition/" + conditionid + "/"
    payload = {
         "condition_name":"测试文本相似度",
         "condition_description":"这个条件是文本相似度的",
         "operator":"op004_0.6",
         "text_scope":"1|-1",
         "role_scope": 1,
         "reference_content":"我们公司会帮您解决"
    }
    headers = {
        'Content-Type': "application/json",
        'Accept-Charset': "utf-8",
    }
    response = requests.request("PUT", url, data=json.dumps(payload), headers=headers)
    print(response.text)

def test_delete_condition(url,conditionid):
    url = url + "/condition/" + conditionid + "/"
    headers = {
        'Content-Type': "application/json",
        'Accept-Charset': "utf-8",
    }
    response = requests.request("DELETE", url, headers=headers)
    print(response.text)

def test_analysis(url):
    url = url + "/analysis/"
    payload = {
                "siteid": "x888",
                "converids": [
                                {
                                    "converid": "h1001",
                                    "messages": [
                                        {
                                            "messageid": "m1001",
                                            "fromuser": "c1001",
                                            "createat": 12345,
                                            "type": 1,
                                            "message": "你好，欢迎咨询客服热线，很高兴为你服务。请问有什么可以帮助您的？我会为你及时解答你的疑问。"

                                        },
                                        {
                                            "messageid": "m1002",
                                            "fromuser": "c1002",
                                            "createat": 12388,
                                            "type": 2,
                                            "message": "你们的产品优点偏贵，可以便宜点吗？你们家的产品有什么优惠，售后服务怎么样。我们公司希望能拿到性价比高的产品"

                                        },
                                        {
                                            "messageid": "m1003",
                                            "fromuser": "c1001",
                                            "createat": 12500,
                                            "type": 1,
                                            "message": "你的心情我们可以理解，每个买家都希望用最少的钱买到最好的服务。这是每一个买家的心声。我们作为厂家首先是产品的品质您可以放心，其次我们的售前售后服务一定会让你满意。只要你不满意我们的产品，都是无理由退货的。"

                                        }
                                    ]
                                },
                ]
            }
    headers = {
        'Content-Type': "application/json",
        'Accept-Charset': "utf-8",
    }
    response = requests.request("POST", url, data=json.dumps(payload), headers=headers)
    print(response.text)

def test_create_task(url):
    url = url  + "/task/"
    payload = {
                "site_id": "kf_888",
                "task_name": "任务3",
                "start_time": "",
                "end_time": "",
                "monitor_type": "哈哈",
                "transaction_id": "qwed"
            }
    headers = {
        'Content-Type': "application/json",
        'Accept-Charset': "utf-8",
    }
    response = requests.request("POST", url, data=json.dumps(payload), headers=headers)
    print(response.text)

def test_update_task(url,taskid):
    url = url  + "/task/" + taskid + "/"
    payload = {
                "site_id": "kf_888",
                "task_name": "任务4",
                "start_time": "2018-10-1",
                "end_time": "2018-10-2",
                # "monitor_type": ,
                "transaction_id": ""
            }
    headers = {
        'Content-Type': "application/json",
        'Accept-Charset': "utf-8",
    }
    response = requests.request("PUT", url, data=json.dumps(payload), headers=headers)
    print(response.text)

def test_delete_task(url,taskid):
    url = url  + "/task/" + taskid + "/"
    headers = {
        'Content-Type': "application/json",
        'Accept-Charset': "utf-8",
    }
    response = requests.request("DELETE", url, headers=headers)
    print(response.text)


if __name__ == '__main__':
    #test_create_rule(URL)
    #test_update_rule(URL,qualityId)
    #test_delete_rule(URL, 'e782c006')
    #test_create_condition(URL)
    #test_update_condition(URL, conditionId)
    #test_delete_condition(URL, '0b9ac7d2')
    #test_analysis(URL)
    #test_create_task(TASKURL)
    #test_update_task(TASKURL,'6e15b9c8')
    test_delete_task(TASKURL,'6e15b9c8')



"""
发送给分析模块的数据：
{
    'siteid': 'kf_8006',
    'converids': [
                    {
                        'converid': 'kf_8006_template_10_1533286799069109747',
                        'messages': [
                            {'createat': 1533286803696, 'messageid': '1533286803696WEB', 'msgtype': 11, 'type': None, 'message': '哈哈'},
                            {'createat': 1533286811506, 'messageid': '1533286811506WEB', 'msgtype': 11, 'type': None, 'message': '你好呀'},
                            {'createat': 1533286799503, 'messageid': 'D15332867995029d4d75d46', 'msgtype': 11, 'type': None, 'message': 'aaaaaaaaaaaaa'}
                        ],
                    },
                    {
                        'converid': 'kf_8006_template_10_1533295528749347484',
                        'messages':  [
                            { "messageid": "1533286803696WEB", "msgtype": 11,"createat": 1533286803696,"type": null,"message": "哈哈"},
                            {"messageid": "1533286811506WEB","msgtype": 11,"createat": 1533286811506, "type": null, "message": "你好呀"},
                        ]
                    }
                ],
    }

#质检结果
{
    "msg": "质检完成",
    "code": 0,
    "data": [
        {
            "converid": "kf_8006_template_10_1533286799069109747",
            "grade": -20,
            "rule_list": [
                {
                    "ruleid": "25490864",
                    "hit_rule_message": [
                        "1533286811506WEB"
                    ]
                }
            ],
        },
        {
            "converid": "kf_8006_template_10_1533295528749347484",
            "grade": -20,
            "rule_list": [
                {
                    "ruleid": "25490864",
                    "hit_rule_message": [
                        "1533295691932WEB"
                    ]
                }
            ],
           
        },
        {
            "converid": "kf_8006_template_7_1533299229613750689",
            "grade": 0,
            "rule_list": [
                {
                    "ruleid": "25490864",
                    "hit_rule_message": []
                }
            ],
          
        }
    ],
}
"""

