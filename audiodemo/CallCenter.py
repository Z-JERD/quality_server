import requests
import os
import json
import uuid
from aip import AipSpeech


CALL_APP_ID = 15146084
CALL_API_KEY = 'QYUQ1DGS5mzX5VK1uPsYsRZz'
CALL_SECRET_KEY = 'XNfnUDiyZIsYPx8RcbnfH3GOIGYvXPIH'
companyName = 'xiaoneng'
audiotype = 'pcm'
Token_request_url = "https://aip.baidubce.com/oauth/2.0/token"
Upload_request_url = "https://aip.baidubce.com/rpc/2.0/session/offline/upload/asr?access_token"
result_request_url = "https://aip.baidubce.com/rpc/2.0/search/info?access_token"
Token_payload = {
    'grant_type': 'client_credentials',
    'client_id':CALL_API_KEY,
    'client_secret':CALL_SECRET_KEY
}

class  BaseResponse(object):
    def __init__(self):
        self.data = None
        self.msg = ""
        self.code = 3000
    @property
    def dict(self):
        return self.__dict__


class CallCenterDeal:

    def __init__(self):
        self.CALL_APP_ID =  CALL_APP_ID
        self.CALL_API_KEY = CALL_API_KEY
        self.CALL_SECRET_KEY = CALL_SECRET_KEY
        self.companyName = companyName
        self.audiotype = audiotype
        self.Token_request_url = Token_request_url
        self.Upload_request_url = Upload_request_url
        self.result_request_url = result_request_url
        self.Token_payload = Token_payload

    def audiotopcm(self,audio_file_path):
        '''
        mp3音频转换pcm音频
        '''
        response = BaseResponse()
        pcm_name = audio_file_path.replace('mp3','pcm')
        cmd_str = "ffmpeg -y  -i {file_name} -acodec pcm_s16le -f s16le -ac 1 -ar 8000 {pcm_name}".format(
            file_name = audio_file_path,pcm_name = pcm_name)
        try:
            os.system(cmd_str)
        except Exception as e:
            response.code = 3001
            response.msg = '音频转换失败'
        else:
            response.code = 3000
            response.msg = '音频解析成功'
            response.data = pcm_name
        return response.dict

    def getbaidutoken(self):
        response = BaseResponse()
        try:
            request_response = requests.post(self.Token_request_url, data = self.Token_payload)
        except Exception as e:
            response.code = 3101
            response.msg = 'token获取失败'
        else:
            data = json.loads(request_response.text)
            access_token = data.get('access_token')
            expires_in = data.get('expires_in')
            if not access_token and not expires_in:
                response.code = 3102
                response.msg = 'API Key/Secret Key有误'
            else:
                response_data = {
                    'access_token': access_token,
                    'expires_in ': expires_in
                }
                response.code = 3000
                response.msg = 'token获取成功'
                response.data = response_data
        return response.dict

    def uploadaudio(self, access_token,audiourl):
        response = BaseResponse()
        callId = str(uuid.uuid4())
        print(callId)
        Upload_request_url = self.Upload_request_url + '=' + access_token
        Upload_payload = {
            "appId": self.CALL_APP_ID,
            "companyName": self.companyName,
            "callId": callId,
            "agentFileUrl": audiourl,
            "suffix": self.audiotype
        }
        try:
            upload_reponse = requests.post(Upload_request_url, data = json.dumps(Upload_payload))
        except Exception as e:
            response.code = 3201
            response.msg = '上传音频文件失败'
        else:
            upload_data = json.loads(upload_reponse.text)
            status = upload_data.get('status')
            msg = upload_data.get('msg')
            if not status and msg == 'OK':
                response.code = 3000
                response.msg = '上传音频文件成功'
                response.data = {'callId':callId}
            elif status == 50000:
                response.code = 3202
                response.msg = 'appId或callId无效'
            elif status == 50008:
                response.code = 3203
                response.msg = '上传音频url有误'
            elif status == 50011:
                response.code = 3204
                response.msg = '音频类型不是av或pcm'
            elif status == 9999:
                response.code = 3205
                response.msg = '请求参数错误'
            else:
                response.code = 3206
                response.msg = '请求参数错误'
        return response.dict

    def getresultquery(self,access_token,callId):
        response = BaseResponse()
        result_request_url = self.result_request_url + '=' + access_token
        result_request_payload = {
            "category": "OFFLINE_ASR_RESULT",
            "paras": {
                "appId": self.CALL_APP_ID,
                "callId": callId,
            }
        }
        try:
            result_reponse = requests.post(result_request_url, data = json.dumps(result_request_payload))
        except Exception as e:
            response.code = 3203
            response.msg = '结果查询失败'
        else:
            result_data = json.loads(result_reponse.text)
            status = result_data.get('status')
            msg = result_data.get('msg')
            if not status and msg == 'OK':
                content_data = result_data.get('data')
                response.code = 3000
                response.msg = '获取结果成功'
                response.data = {'content_data': content_data}
            elif status == 50000:
                response.code = 3302
                response.msg = 'appId或callId无效'
            elif status == 50002:
                response.code = 3303
                response.msg = '文件URL下载失败'
            elif status == 50003:
                response.code = 3304
                response.msg = '采样率/位深设置有误'
            elif status == 50007:
                response.code = 3305
                response.msg = '翻译过程出现异常'
            elif status == 9999:
                response.code = 3206
                response.msg = '系统错误/请求参数错误'
            else:
                response.code = 3207
                response.msg = '正在翻译,请耐心等待翻译结果'
        return response.dict



if __name__ == "__main__":
    # file_name = '1810161549527452000100450002142a.mp3'
    # audiourl = "http://bj-v100.ntalker.com/setting/pcm/salesman.wav"
    # calldeal_object = CallCenterDeal()
    # #转换音频格式
    # #audiotopcm_response = calldeal_object.audiotopcm(file_name)
    # #获取token
    # token_response = calldeal_object.getbaidutoken()
    # token_code = token_response.get('code')
    # if token_code == 3000:
    #     token_data = token_response.get('data')
    #     token = token_data.get('access_token')
    #     #上传音频
    #     uploadaudio_response = calldeal_object.uploadaudio(token,audiourl)
    #     uploadaudio_code = uploadaudio_response('code')
    #     if uploadaudio_code == 3000:
    #         uploadaudio_data = uploadaudio_response.get('data')
    #         callId = uploadaudio_data.get('callId')
    #         #获取音频转换结果
    #         getresult_response = calldeal_object.getresultquery(token,callId)
    #         getresult_code = getresult_response.get('code')
    #         if getresult_code == 3000:
    #             getresult_data = getresult_response.get('data')
    #             content_data = getresult_data.get('content_data')
    #             print(content_data)
    #         else:print(getresult_response)
    #     else:print(uploadaudio_response)
    # else:print(token_response)
    companyName = 'xiaoneng'
    suffix = 'wav'
    CALL_APP_ID = 15146084
    CALL_API_KEY = 'QYUQ1DGS5mzX5VK1uPsYsRZz'
    CALL_SECRET_KEY = 'XNfnUDiyZIsYPx8RcbnfH3GOIGYvXPIH'
    Token_request_url = "https://aip.baidubce.com/oauth/2.0/token"
    Upload_request_url = "https://aip.baidubce.com/rpc/2.0/session/offline/upload/asr?access_token"
    result_request_url = "https://aip.baidubce.com/rpc/2.0/search/info?access_token"
    KEY_TASK_Content = 'content'
    Token_payload = {
        'grant_type': 'client_credentials',
        'client_id': CALL_API_KEY,
        'client_secret': CALL_SECRET_KEY
    }


    try:
        r = requests.post(Token_request_url, data=Token_payload)
    except Exception as e:
        print(e)
    data = json.loads(r.text)
    access_token = data.get('access_token')

    #callId = '4e8695cb-8cc7-467d-9a05-c1b083a5e441'
    #双侧
    callId = 'bda28e8b-6cf2-45fc-8eaf-37012e142e8e'

    result_request_url = result_request_url + '=' + access_token

    result_request_payload = {
        "category": "OFFLINE_ASR_RESULT",
        "paras": {
            "appId": CALL_APP_ID,
            "callId": callId,
        }
    }
    try:
        result_reponse = requests.post(result_request_url, data=json.dumps(result_request_payload))
    except Exception as e:
        print(e)
    result_data = json.loads(result_reponse.text)
    print('the result of search is：', result_data)
    # Content_list = result_data.get('data')[KEY_TASK_Content]
    #
    # Agent_Data = [Content['sentence'] for Content in json.loads(Content_list) if Content['roleCategory'] == 'agent']
    # client_Data = [Content['sentence'] for Content in json.loads(Content_list) if Content['roleCategory'] == 'client']
    # Agent_Result = ''.join(Agent_Data)
    # client_Result = ''.join(client_Data)
    # print(Agent_Result)
    # print(client_Result)









