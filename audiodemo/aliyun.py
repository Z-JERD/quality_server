# -*- coding: utf8 -*-
import json
import time
from aliyunsdkcore.acs_exception.exceptions import ClientException
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
def fileTrans(akId, akSecret, appKey, fileLink) :
    REGION_ID = "cn-shanghai"
    PRODUCT = "nls-filetrans"
    DOMAIN = "filetrans.cn-shanghai.aliyuncs.com"
    API_VERSION = "2018-08-17"
    POST_REQUEST_ACTION = "SubmitTask"
    GET_REQUEST_ACTION = "GetTaskResult"
    KEY_APP_KEY = "app_key"
    KEY_FILE_LINK = "file_link"
    KEY_TASK = "Task"
    KEY_TASK_ID = "TaskId"
    KEY_STATUS_TEXT = "StatusText"
    KEY_TASK_Result = 'Result'
    # 创建AcsClient实例
    client = AcsClient(akId, akSecret, REGION_ID)
    # 创建提交录音文件识别请求，并设置请求参数
    postRequest = CommonRequest()
    postRequest.set_domain(DOMAIN)
    postRequest.set_version(API_VERSION)
    postRequest.set_product(PRODUCT)
    postRequest.set_action_name(POST_REQUEST_ACTION)
    postRequest.set_method('POST')
    task = {KEY_APP_KEY : appKey, KEY_FILE_LINK : fileLink}
    task = json.dumps(task)
    postRequest.add_body_params(KEY_TASK, task)
    try :
        # 提交录音文件识别请求，处理服务端返回的响应
        postResponse = client.do_action_with_exception(postRequest)
        postResponse = json.loads(postResponse.decode('utf_8'))
        print (postResponse)
        # 获取录音文件识别请求任务的ID，以供识别结果查询使用
        taskId = ""
        statusText = postResponse[KEY_STATUS_TEXT]
        if statusText == "SUCCESS" :
            print ("录音文件识别请求成功响应！")
            taskId = postResponse[KEY_TASK_ID]
        else :
            print ("录音文件识别请求失败！")
            return
    except ServerException as e:
        print (e)
    except ClientException as e:
        print (e)
    # 创建识别结果查询请求，设置查询参数为任务ID
    getRequest = CommonRequest()
    getRequest.set_domain(DOMAIN)
    getRequest.set_version(API_VERSION)
    getRequest.set_product(PRODUCT)
    getRequest.set_action_name(GET_REQUEST_ACTION)
    getRequest.set_method('GET')
    getRequest.add_query_param(KEY_TASK_ID, taskId)
    # 提交录音文件识别结果查询请求
    # 以轮询的方式进行识别结果的查询，直到服务端返回的状态描述符为"SUCCESS"、"SUCCESS_WITH_NO_VALID_FRAGMENT"，
    # 或者为错误描述，则结束轮询。
    statusText = ""
    while True :
        try :
            getResponse = client.do_action_with_exception(getRequest)
            getResponse = json.loads(getResponse.decode('utf_8'))
            #print(getResponse)
            # Sentences = getResponse.get('Result')
            # print(Sentences)
            # Result = [data.Text for data in Sentences]
            # print (Result)

            statusText = getResponse[KEY_STATUS_TEXT]
            if statusText == "RUNNING" or statusText == "QUEUEING" :
                # 继续轮询
                time.sleep(3)
            else :
                # 退出轮询
                break
        except ServerException as e:
            print (e)
        except ClientException as e:
            print (e)
    if statusText == "SUCCESS" or statusText == "SUCCESS_WITH_NO_VALID_FRAGMENT" :
        print ("录音文件识别成功！")
        print(getResponse)
        Result_list = getResponse[KEY_TASK_Result]
        Result = [data['Text'] for data in Result_list['Sentences'] ]
        print(Result)
    else :
        print ("录音文件识别失败！")
    return
accessKeyId = "LTAIldDpwnTsxtLc"
accessKeySecret = "rEeWreRNqFm7qSRsPpDHs3D7OE1frJ"
appKey = "VORAlRxD5emkRm5f"
#fileLink = "https://aliyun-nls.oss-cn-hangzhou.aliyuncs.com/asr/fileASR/examples/nls-sample-16k.wav"
fileLink = "http://bj-v100.ntalker.com/setting/pcm/8k.wav"
# 执行录音文件识别
start_time = time.time()
fileTrans(accessKeyId, accessKeySecret, appKey, fileLink)
end_time = time.time()
print('time consuming is ',end_time - start_time)